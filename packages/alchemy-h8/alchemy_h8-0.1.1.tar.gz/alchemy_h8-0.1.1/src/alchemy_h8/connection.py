import asyncio
import logging
import secrets
import signal
import sys
import time
import weakref
from contextlib import asynccontextmanager
from typing import (
    Any,
    AsyncGenerator,
    Dict,
    List,
    Optional,
    TypeVar,
)

import structlog
from sqlalchemy import event, text
from sqlalchemy.exc import SQLAlchemyError, TimeoutError
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from tenacity import (
    AsyncRetrying,
    RetryCallState,
    RetryError,
    before_sleep_log,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
    wait_random,
)

from src.alchemy_h8.circuit_breaker import CircuitBreaker, CircuitBreakerState
from src.alchemy_h8.config import DBConnectionConfig
from src.alchemy_h8.rate_limiter import RateLimiter, RateLimiterError

T = TypeVar("T")


class DBConnectionHandler:
    """Manages database connections with advanced features like:
    - Connection pooling with optimal configuration
    - Circuit breaker pattern for fault tolerance
    - Rate limiter for throttling excessive requests
    - Retry logic with exponential backoff
    - Read/write splitting
    - Secure credential handling
    - Task cancellation protection
    - Graceful shutdown support
    """

    def __init__(self, config: DBConnectionConfig, logger: Any = None):
        """Initialize connection handler with provided configuration."""
        self.logger = logger or structlog.get_logger()  # Fixed get_self.logger() typo
        self.config = config
        self._async_engine: Optional[AsyncEngine] = None
        self._async_read_replicas: List[AsyncEngine] = []
        self._lock = asyncio.Lock()

        # Connection tracking for cleanup
        self._active_connections: Dict[int, AsyncConnection] = {}
        self._connection_track_lock = asyncio.Lock()

        # Connection lifecycle timing
        self._connection_creation_times: Dict[int, float] = {}
        self._long_lived_threshold = 300  # 5 minutes in seconds
        self._max_safe_connection_lifetime = 3600  # 1 hour in seconds

        # Track connection counts for diagnostics
        self._total_connections_created = 0
        self._total_connections_released = 0
        self._max_tracked_connections = 0

        # Optional circuit breaker
        self._circuit_breaker = None
        if config.use_circuit_breaker:
            self._circuit_breaker = CircuitBreaker(
                failure_threshold=config.circuit_breaker_threshold,
                recovery_timeout=config.circuit_breaker_recovery_timeout,
            )
            self.logger.info(f"Circuit breaker enabled with failure threshold {config.circuit_breaker_threshold}, recovery timeout {config.circuit_breaker_recovery_timeout}s")
        else:
            self.logger.info("Circuit breaker disabled")

        # Optional rate limiter
        self._rate_limiter = None
        if config.use_rate_limiter:
            self._rate_limiter = RateLimiter(
                max_requests=config.rate_limit_max_requests,
                time_window=config.rate_limit_time_window,
                strategy=config.rate_limit_strategy,
                max_delay=config.rate_limit_max_delay,
                enabled=True,
            )
            self.logger.info(f"Rate limiter enabled with {config.rate_limit_max_requests} requests per {config.rate_limit_time_window}s window, strategy: {config.rate_limit_strategy.value}")
        else:
            self.logger.info("Rate limiter disabled")

        # Connection limiting semaphores for backpressure
        self._async_connection_semaphore: Optional[asyncio.Semaphore] = None  # Will be initialized with async engine
        self._connection_attempts = 0
        self._async_connection_lock = asyncio.Lock()

        # Retry configuration for connection attempts
        self._max_retries = config.max_retries
        self._base_retry_delay = config.base_retry_delay
        self._max_retry_delay = config.max_retry_delay
        self._retry_jitter = config.retry_jitter

        # Idle connection tracking
        self._idle_connection_timeout = config.idle_connection_timeout
        self._idle_connection_check_task: Optional[asyncio.Task[Any]] = None

        # Background tasks tracking
        self._background_tasks: set[asyncio.Task[Any]] = set()

        # Add round-robin counter for read replicas
        self._replica_counter = 0
        self._replica_counter_lock = asyncio.Lock()

    async def initialize(self) -> None:
        """Initialize database engines asynchronously."""
        await self._initialize_engines()
        # Start idle connection management if enabled
        if self._idle_connection_timeout > 0:
            self._start_idle_connection_management()
        # Start periodic stale connection check
        self._start_stale_connection_check()

    def _start_idle_connection_management(self) -> None:
        """Start background task to monitor and close idle connections."""
        if self._idle_connection_check_task is None:
            _ = asyncio.get_running_loop()
            task = asyncio.create_task(self._manage_idle_connections())
            self._background_tasks.add(task)
            # Remove task from set when completed
            task.add_done_callback(self._background_tasks.discard)
            self._idle_connection_check_task = task
            self.logger.info(f"Idle connection management started with timeout of {self._idle_connection_timeout}s")

    async def _manage_idle_connections(self) -> None:
        """Background task to periodically check and close idle connections."""
        try:
            check_interval = min(self._idle_connection_timeout / 2, 300)  # Check at half the timeout or max 5 minutes
            while True:
                await asyncio.sleep(check_interval)
                if self._async_engine:
                    # Since we can't directly access idle connections count,
                    # we'll use a dispose(close=False) periodically to reset idle connections
                    self.logger.info("Idle connection check: pruning excess idle connections")
                    # This uses SQLAlchemy's built-in pruning mechanism
                    await self._async_engine.dispose(close=False)
                    self.logger.info("Idle connections pruned")
        except asyncio.CancelledError:
            self.logger.debug("Idle connection management task cancelled")
        except Exception as e:
            self.logger.error(f"Error in idle connection management: {str(e)}")

    async def _initialize_engines(self) -> None:
        """Initialize database engines based on configuration."""
        if not self._async_engine:
            self._async_engine = self._create_engine(self.config)
            self._setup_engine_events(self._async_engine)

            # Initialize connection semaphore based on pool size
            max_connections = self.config.pool_size + self.config.max_overflow
            # Use 80% of max connections to leave some headroom
            semaphore_value = max(1, int(max_connections * 0.8))
            self._async_connection_semaphore = asyncio.Semaphore(semaphore_value)

            # Test the engine with a simple query to ensure it's ready
            try:
                conn = await self._create_connection_with_retry(self._async_engine)
                try:
                    await conn.execute(text("SELECT 1"))  # type: ignore
                    self.logger.debug("Database connection initialized successfully")
                finally:
                    # Always close the connection when done
                    await conn.close()  # type: ignore
            except Exception as e:
                self.logger.error(f"Failed to initialize database connection: {str(e)}")
                raise

        # Create read replica engines if configured

        if self.config.read_replica_hosts:
            replica_configs = DBConnectionConfig.get_read_replica_host_configs(self.config.read_replica_hosts)
            for replica_config in replica_configs:
                replica_engine = self._create_engine(replica_config)
                self._setup_engine_events(replica_engine)
                self._async_read_replicas.append(replica_engine)

    def _create_engine(self, config: DBConnectionConfig) -> AsyncEngine:
        """Create SQLAlchemy engine based on configuration."""
        conn_string = config.url
        engine_args = config.get_engine_args()

        # Set connection pool health check settings
        engine_args.setdefault("pool_pre_ping", True)  # Enable connection health checks
        engine_args.setdefault("pool_recycle", 3600)  # Recycle connections after 1 hour
        engine_args.setdefault("pool_use_lifo", True)  # Last In First Out for better connection reuse

        # Set echo for debugging if needed
        if hasattr(config, "echo") and config.echo:
            engine_args.setdefault("echo", True)

        # Set pool timeout
        engine_args.setdefault("pool_timeout", config.pool_timeout)

        return create_async_engine(conn_string, **engine_args)

    def _setup_engine_events(self, engine: AsyncEngine) -> None:  # noqa: C901
        """Set up event listeners for the engine."""

        @event.listens_for(engine.sync_engine, "connect")
        def on_connect(dbapi_connection: Any, connection_record: Any) -> None:
            self.logger.debug("New database connection established")

            # Set connection timeout at the driver level if possible
            # This helps prevent connections hanging indefinitely
            try:
                if hasattr(dbapi_connection, "set_session"):
                    # For asyncpg
                    asyncio.create_task(dbapi_connection.set_session(statement_timeout=self.config.statement_timeout * 1000 if hasattr(self.config, "statement_timeout") else 30000))
            except Exception as e:
                self.logger.warning(f"Could not set statement timeout: {str(e)}")

        @event.listens_for(engine.sync_engine, "checkout")
        def on_checkout(dbapi_connection: Any, connection_record: Any, connection_proxy: Any) -> None:
            self.logger.debug("Database connection checked out from pool")

        @event.listens_for(engine.sync_engine, "checkin")
        def on_checkin(dbapi_connection: Any, connection_record: Any) -> None:
            # This event fires when a connection is properly returned to the pool
            # We can remove it from our tracking at this point
            conn_id = id(connection_record.driver_connection)

            async def remove_from_tracking() -> None:
                async with self._connection_track_lock:
                    self._active_connections.pop(conn_id, None)
                    self._total_connections_released += 1

                    # Calculate and log connection lifetime
                    creation_time = self._connection_creation_times.pop(conn_id, None)
                    if creation_time:
                        lifetime = time.time() - creation_time
                        if lifetime > self._long_lived_threshold:
                            self.logger.warning(f"Long-lived connection detected: {lifetime:.2f}s before return to pool")
                        else:
                            self.logger.debug(f"Connection lifetime: {lifetime:.2f}s")

            # Schedule the removal asynchronously
            asyncio.create_task(remove_from_tracking())
            self.logger.debug("Database connection returned to pool")

        # Set up event for connection reset on checkout
        @event.listens_for(engine.sync_engine, "invalidate")
        def on_connection_invalidate(
            dbapi_connection: Any,
            connection_record: Any,
            exception: Optional[Exception],
        ) -> None:
            if exception:
                self.logger.warning(f"Connection invalidated due to error: {str(exception)}")
            else:
                self.logger.info("Connection invalidated")

        # Set up finalizer to catch unclosed connections
        @event.listens_for(engine.sync_engine, "engine_disposed")
        def on_engine_disposed(engine: Any) -> None:
            self.logger.info("Engine disposed, all connections returned to pool")

    async def get_engine(self, read_only: bool = False) -> AsyncEngine:
        """
        Get database engine.

        Args:
            read_only: If True and read replicas are configured, returns a read replica engine.

        Returns:
            SQLAlchemy AsyncEngine instance
        """
        # Initialize engines if needed
        if self._async_engine is None:
            async with self._lock:
                if self._async_engine is None:
                    await self.initialize()

        # For read operations, use read replicas if available and enabled
        if read_only and self._async_read_replicas and self.config.use_read_replicas_for_reads:
            # Use true round-robin with an atomic counter
            async with self._replica_counter_lock:
                replica_index = self._replica_counter % len(self._async_read_replicas)
                self._replica_counter += 1
                self.logger.debug(f"Using read replica {replica_index} From {len(self._async_read_replicas)}")
            return self._async_read_replicas[replica_index]

        if self._async_engine is None:
            raise RuntimeError("Failed to initialize database engine")

        return self._async_engine

    # Helper method for tenacity retry logic
    def _is_transient_error(self, exception: BaseException) -> bool:
        """Check if an exception is a transient error that should be retried."""
        error_msg = str(exception).lower()
        if "connect call failed" in error_msg:
            return True
        if not isinstance(exception, SQLAlchemyError):
            return False

        return any(
            msg in error_msg
            for msg in [
                "could not connect",
                "connection refused",
                "connection timed out",
                "too many connections",
                "connection has been closed",
                "connection reset",
                "operational error",
                "temporarily unavailable",
                "broken pipe",
            ]
        )

    # Helper method for retry before_sleep logging
    def _log_retry_attempt(self, retry_state: RetryCallState) -> None:
        """Log retry attempts."""
        if retry_state.outcome is not None and retry_state.outcome.failed:
            exception = retry_state.outcome.exception()
            if retry_state.next_action is not None:
                self.logger.warning(f"Transient database error (attempt {retry_state.attempt_number}/{self._max_retries}): {str(exception)}. Retrying in {retry_state.next_action.sleep} seconds")
            else:
                self.logger.warning(f"Transient database error (attempt {retry_state.attempt_number}/{self._max_retries}): {str(exception)}. No more retries.")

    # Helper method to create tenacity retry configuration
    def _get_retry_config(self) -> Dict[str, Any]:
        """Get Tenacity retry configuration based on class settings."""
        return {
            "retry": retry_if_exception(self._is_transient_error),
            "stop": stop_after_attempt(self._max_retries),
            "wait": wait_exponential(
                multiplier=self._base_retry_delay,
                min=self._base_retry_delay,
                max=self._max_retry_delay,
            )
            + wait_random(0, self._retry_jitter),
            "before_sleep": before_sleep_log(self.logger, logging.WARNING),
            "reraise": True,
        }

    # Helper method for creating a connection with retries
    async def _create_connection_with_retry(self, engine: AsyncEngine) -> Optional[AsyncConnection]:
        """Create a database connection with retry logic."""
        retry_config = self._get_retry_config()

        try:
            async for attempt in AsyncRetrying(**retry_config):
                with attempt:
                    try:
                        conn = await engine.connect()
                        # Register the connection for tracking
                        await self._register_connection(conn)
                        # Record success for circuit breaker if enabled
                        if self._circuit_breaker:
                            self._circuit_breaker.record_success()
                        return conn
                    except Exception:
                        # Record failure only on the last attempt
                        if attempt.retry_state.attempt_number >= self._max_retries:
                            if self._circuit_breaker:
                                self._circuit_breaker.record_failure()
                        raise
            return None  # This line is never reached due to reraise=True, but helps with type checking
        except RetryError as e:
            # If all retry attempts failed
            self.logger.error(f"Database connection failed after {self._max_retries} retries: {str(e.last_attempt.exception())}")
            # Record failure for circuit breaker
            if self._circuit_breaker:
                self._circuit_breaker.record_failure()
            if e.last_attempt and hasattr(e.last_attempt, "exception"):
                exc = e.last_attempt.exception()
                if exc:
                    self.logger.error(f"Max retries exceeded for connection: {str(exc)}")
                    # The correct way to re-raise with chaining
                    raise exc from e
                else:
                    self.logger.error("Max retries exceeded for connection with unknown error")
                    raise RuntimeError("Failed to establish database connection after retries") from e
            else:
                self.logger.error("Max retries exceeded for connection with unknown error")
                raise RuntimeError("Failed to establish database connection after retries") from e

    @asynccontextmanager
    async def get_async_connection(self, read_only: bool = False) -> AsyncGenerator[AsyncConnection, None]:  # noqa: C901
        """
        Get async database connection with retry logic.

        Args:
            read_only: If True and read replicas are configured, gets connection from read replica.

        Yields:
            AsyncConnection object

        Raises:
            CircuitBreakerOpenError: If circuit breaker is open
            RateLimiterError: If rate limit exceeded
            SQLAlchemyError: For database-related errors
        """
        engine = await self.get_engine(read_only)

        # Check circuit breaker if enabled
        if self._circuit_breaker and self._circuit_breaker.state == CircuitBreakerState.OPEN:
            self.logger.warning(f"Circuit breaker is open until {self._circuit_breaker.next_attempt_time}, rejecting connection request")
            if hasattr(self._circuit_breaker, "CircuitBreakerOpenError"):
                raise self._circuit_breaker.CircuitBreakerOpenError(f"Circuit breaker is open until {self._circuit_breaker.next_attempt_time}")
            else:
                raise RuntimeError(f"Circuit breaker is open until {self._circuit_breaker.next_attempt_time}")

        # Apply rate limiting if enabled
        if self._rate_limiter and self._rate_limiter.enabled:
            acquired = await self._rate_limiter.attempt_acquire()
            if not acquired:
                self.logger.warning("Rate limit exceeded, rejecting connection request")
                raise RateLimiterError("Database rate limit exceeded, try again later")

        # Apply connection limiting with semaphore for backpressure
        if self._async_connection_semaphore is None:
            async with self._async_connection_lock:
                if self._async_connection_semaphore is None:
                    # Initialize with a small buffer above pool size to allow for some overflow
                    max_conn = self.config.pool_size + min(self.config.max_overflow, 5)
                    self._async_connection_semaphore = asyncio.Semaphore(max_conn)

        try:
            # Try to acquire a semaphore slot - this provides backpressure
            # when too many concurrent connections are attempted
            async with self._async_connection_lock:
                self._connection_attempts += 1
                current_attempts = self._connection_attempts

            # Add jitter to prevent thundering herd problem
            if current_attempts > self.config.pool_size:
                jitter = secrets.randbits(12) / 1000
                await asyncio.sleep(jitter)

            # Try to acquire the semaphore with a timeout
            timeout = self.config.pool_timeout * 0.8  # Slightly shorter than pool timeout
            try:
                acquired = False

                # Ensure semaphore exists
                if self._async_connection_semaphore is None:
                    raise RuntimeError("Connection semaphore not initialized")

                async with asyncio.timeout(timeout):
                    acquired = await self._async_connection_semaphore.acquire()

                if not acquired:
                    raise TimeoutError("Failed to acquire connection semaphore")
            except (asyncio.TimeoutError, TimeoutError) as e:
                self.logger.warning(f"Connection semaphore acquisition timed out after {timeout}s")
                raise TimeoutError(f"Database connection pool exhausted. Too many concurrent connections. Max pool size: {self.config.pool_size}, Current attempts: {current_attempts}") from e

            # Use tenacity for connection retry logic
            try:
                conn = await self._create_connection_with_retry(engine)
                if conn is None:
                    raise RuntimeError("Failed to create database connection")

                try:
                    yield conn
                finally:
                    # Always close the connection to return it to the pool
                    try:
                        await asyncio.shield(conn.close())
                    except Exception as e:
                        self.logger.error(f"Error closing connection: {str(e)}")
            except Exception as e:
                self.logger.error(f"Failed to establish database connection: {str(e)}")
                raise

        finally:
            async with self._async_connection_lock:
                self._connection_attempts -= 1

            # Always release the semaphore if it was acquired
            if self._async_connection_semaphore is not None:
                # No need for checking value, just release
                self._async_connection_semaphore.release()

    async def get_async_session_maker(self, read_only: bool = False, **kwargs: Any) -> async_sessionmaker[AsyncSession]:
        """
        Get a session maker for creating async SQLAlchemy ORM sessions.

        Args:
            read_only: If True and read replicas are configured, creates sessions connected to read replicas
            **kwargs: Additional arguments for async_sessionmaker

        Returns:
            SQLAlchemy async_sessionmaker instance
        """
        engine = await self.get_engine(read_only)
        session_args = {
            "expire_on_commit": False,  # Prevent detachment of objects after commit
            **kwargs,
        }
        return async_sessionmaker(engine, **session_args)

    @asynccontextmanager
    async def async_session_scope(self, read_only: bool = False, **session_kwargs: Any) -> AsyncGenerator[AsyncSession, None]:  # noqa: C901
        """
        Provide an async transactional scope around a series of operations.

        Args:
            read_only: If True and read replicas are configured, uses a read replica engine
            **session_kwargs: Additional args for AsyncSession creation

        Yields:
            SQLAlchemy AsyncSession object
        """
        # Check circuit breaker state before creating a session
        if self._circuit_breaker and self._circuit_breaker.state == CircuitBreakerState.OPEN:
            if hasattr(self._circuit_breaker, "CircuitBreakerOpenError"):
                raise self._circuit_breaker.CircuitBreakerOpenError(f"Circuit breaker is open until {self._circuit_breaker.next_attempt_time}")
            else:
                raise RuntimeError(f"Circuit breaker is open until {self._circuit_breaker.next_attempt_time}")

        # Apply rate limiting if enabled
        if self._rate_limiter and self._rate_limiter.enabled:
            acquired = await self._rate_limiter.attempt_acquire()
            if not acquired:
                self.logger.warning("Rate limit exceeded, rejecting session request")
                raise RateLimiterError("Database rate limit exceeded, try again later")

        session_maker = await self.get_async_session_maker(read_only, **session_kwargs)
        session = session_maker()

        # Create a wrapper for session.execute to apply rate limiting on queries if needed
        original_execute = session.execute

        async def execute_with_rate_limit(*args: Any, **kwargs: Any) -> Any:
            # Apply per-query rate limiting if enabled
            if self._rate_limiter and self._rate_limiter.enabled:
                acquired = await self._rate_limiter.attempt_acquire()
                if not acquired:
                    self.logger.warning("Per-query rate limit exceeded")
                    raise RateLimiterError("Database rate limit exceeded, try again later")
            try:
                result = await original_execute(*args, **kwargs)
                return result
            except Exception as e:
                # Record failure for circuit breaker if enabled
                if self._circuit_breaker:
                    self._circuit_breaker.record_failure()
                self.logger.error(f"Query execution error: {str(e)}")
                raise

        # Replace the execute method with our rate-limited version
        session.execute = execute_with_rate_limit  # type: ignore[method-assign]

        try:
            yield session
            try:
                # Shield the commit operation from cancellation to prevent connection leaks
                await asyncio.shield(session.commit())

                # Record success for circuit breaker if enabled
                if self._circuit_breaker:
                    self._circuit_breaker.record_success()

            except asyncio.CancelledError:
                self.logger.warning("Task cancelled during commit, ensuring proper cleanup")
                try:
                    # Shield the rollback operation from cancellation
                    await asyncio.shield(session.rollback())
                except Exception as e:
                    self.logger.error(f"Error during rollback after cancellation: {str(e)}")
                raise  # Re-raise the cancellation
            except SQLAlchemyError as e:
                self.logger.error(f"Error committing transaction: {str(e)}")
                try:
                    # Shield the rollback operation from cancellation
                    await asyncio.shield(session.rollback())
                except Exception as rollback_error:
                    self.logger.error(f"Error during rollback: {str(rollback_error)}")
                # Re-raise the original commit error
                raise
        except TimeoutError as e:
            # Explicitly handle pool timeouts
            self.logger.warning(f"Session timeout error: {str(e)}")
            try:
                # Shield the rollback operation from cancellation
                await asyncio.shield(session.rollback())
            except Exception as rollback_error:
                self.logger.error(f"Error during rollback after timeout: {str(rollback_error)}")
            raise
        except asyncio.CancelledError:
            # Handle task cancellation during session usage (before commit)
            self.logger.warning("Task cancelled during session usage, ensuring proper cleanup")
            try:
                # Shield the rollback operation from cancellation
                await asyncio.shield(session.rollback())
            except Exception as e:
                self.logger.error(f"Error during rollback after cancellation: {str(e)}")
            raise  # Re-raise the cancellation
        except Exception:
            # Handle any other exceptions that occurred during session usage
            if self._circuit_breaker:
                self._circuit_breaker.record_failure()

            try:
                # Shield the rollback operation from cancellation
                await asyncio.shield(session.rollback())
            except Exception as rollback_error:
                self.logger.error(f"Error during rollback after exception: {str(rollback_error)}")
            # Re-raise the original exception
            raise
        finally:
            # Restore original execute method
            session.execute = original_execute  # type: ignore[method-assign]

            # Ensure session is closed in all cases, protected from cancellation
            try:
                await asyncio.shield(session.close())
            except Exception as close_error:
                self.logger.error(f"Error closing session: {str(close_error)}")

    async def dispose_gracefully(self) -> None:
        """
        Gracefully close all database connections and dispose of engines.
        This should be called when the application is shutting down.
        """
        try:
            self._cancel_background_tasks()
            self.logger.info("Starting graceful disposal of database connections")

            # Clean up any tracked connections before engine disposal
            async with self._connection_track_lock:
                active_conns = list(self._active_connections.values())
                for conn in active_conns:
                    try:
                        await conn.close()
                    except Exception as e:
                        self.logger.warning(f"Error closing connection during shutdown: {str(e)}")
                self._active_connections.clear()

            # Dispose main engine
            if self._async_engine:
                await self._async_engine.dispose()
                self.logger.info("Successfully disposed main engine connections")

            # Dispose read replica engines
            for replica_engine in self._async_read_replicas:
                try:
                    await replica_engine.dispose()
                except Exception as e:
                    self.logger.warning(f"Error disposing read replica engine: {str(e)}")

            self._async_read_replicas = []
            self.logger.info("Database connections disposed")
        except Exception as e:
            self.logger.error(f"Error during graceful disposal: {str(e)}")
            # Attempt force dispose in case of error
            if self._async_engine:
                try:
                    await self._async_engine.dispose()
                except Exception as e:
                    self.logger.warning(f"Error disposing main engine during force dispose: {str(e)}")
                    pass

    def _cancel_background_tasks(self) -> None:
        """Cancel all background tasks to ensure clean shutdown."""
        for task in self._background_tasks:
            if not task.done():
                task.cancel()
        # Clear the set
        self._background_tasks.clear()
        self.logger.info("Background tasks canceled")

    def setup_signal_handlers(self, loop: Optional[asyncio.AbstractEventLoop] = None) -> None:
        """
        Set up signal handlers for graceful shutdown on SIGTERM and SIGINT.

        This method should be called early in your application startup to ensure
        database connections are properly closed on application shutdown.

        Args:
            loop: Optional event loop to register signal handlers on, defaults to current loop
        """
        _platform = sys.platform.lower()
        self.logger.info(f"Setting up signal handlers for platform {_platform}")
        if _platform == "win32" or _platform == "cygwin" or _platform == "msys":
            self.logger.warning("Signal handlers not supported on Windows")
            return
        loop_to_use: Optional[asyncio.AbstractEventLoop] = loop
        if loop_to_use is None:
            try:
                loop_to_use = asyncio.get_running_loop()
            except RuntimeError:
                self.logger.warning("No running event loop found, signal handlers not registered")
                return

        async def handle_shutdown(sig_name: str) -> None:
            """Handle shutdown signal by disposing connections gracefully."""
            self.logger.info(f"Received {sig_name}, shutting down database connections gracefully")
            await self.dispose_gracefully()
            self.logger.info("Database shutdown complete")

        # Register signal handlers
        for sig_name in ("SIGTERM", "SIGINT"):
            try:
                # Get the signal number from the signal name
                sig = getattr(signal, sig_name)
                if loop_to_use is not None:
                    callback = lambda s=sig_name: asyncio.create_task(handle_shutdown(s))  # noqa: E731
                    loop_to_use.add_signal_handler(sig, callback)
                    self.logger.info(f"Registered {sig_name} handler for graceful database shutdown")
            except (AttributeError, NotImplementedError, ValueError) as e:
                self.logger.warning(f"Failed to register {sig_name} handler: {str(e)}")

    async def _register_connection(self, conn: AsyncConnection) -> None:
        """Register a connection for tracking."""
        async with self._connection_track_lock:
            conn_id = id(conn)
            self._active_connections[conn_id] = conn
            self._connection_creation_times[conn_id] = time.time()

            # Update tracking metrics
            self._total_connections_created += 1
            tracked_count = len(self._active_connections)
            if tracked_count > self._max_tracked_connections:
                self._max_tracked_connections = tracked_count

            # Use weakref to detect when connection might be garbage collected
            # This creates a callback that runs when the connection is about to be collected
            _ = weakref.ref(conn, lambda _: asyncio.create_task(self._cleanup_connection(conn_id)))

            # We'll rely on the SQLAlchemy connection pool events to track connections properly
            # The checkin event in _setup_engine_events will let us know when connections
            # are properly returned to the pool

    async def _cleanup_connection(self, conn_id: int) -> None:
        """Clean up a connection that might have been garbage collected."""
        async with self._connection_track_lock:
            conn = self._active_connections.pop(conn_id, None)
            if conn:
                try:
                    # Don't call close directly - that's what got us in trouble
                    # Instead, tell SQLAlchemy to reclaim this connection
                    self.logger.info(f"Connection {conn_id} was not properly closed, returning to pool")
                    # Add to background tasks to avoid blocking
                    task = asyncio.create_task(self._return_connection_to_pool(conn))
                    self._background_tasks.add(task)
                    task.add_done_callback(self._background_tasks.discard)
                except Exception as e:
                    self.logger.error(f"Error handling leaked connection {conn_id}: {str(e)}")

    async def _return_connection_to_pool(self, conn: AsyncConnection) -> None:
        """Attempt to safely return a connection to the pool."""
        try:
            # Attempt to close the connection with a timeout to prevent hanging
            try:
                # Use shield to protect from cancellation during cleanup
                # Add a timeout to prevent hanging if the connection is in a bad state
                async with asyncio.timeout(3.0):  # 3-second timeout
                    await asyncio.shield(conn.close())
                self.logger.info("Successfully closed leaked connection")
            except (asyncio.TimeoutError, Exception) as e:
                # Log but don't raise - we've tried our best
                self.logger.warning(f"Could not properly close leaked connection: {str(e)}. Will be reclaimed by SQLAlchemy garbage collection")
        except Exception as e:
            self.logger.error(f"Error returning connection to pool: {str(e)}")

    def _start_stale_connection_check(self) -> None:
        """Start background task to check for stale tracked connections."""
        _ = asyncio.get_running_loop()
        task = asyncio.create_task(self._check_stale_connections())
        self._background_tasks.add(task)
        task.add_done_callback(self._background_tasks.discard)
        self.logger.info("Stale connection checker started")

    async def _check_stale_connections(self) -> None:  # noqa: C901
        """Periodically check for stale connections that might be leaked."""
        try:
            # Run every 30 seconds
            check_interval = 30
            while True:
                await asyncio.sleep(check_interval)

                async with self._connection_track_lock:
                    # Copy the keys to avoid modification during iteration
                    connection_ids = list(self._active_connections.keys())

                if connection_ids:
                    self.logger.info(f"Stale connection check: {len(connection_ids)} tracked AsyncConnection objects, created: {self._total_connections_created}, released: {self._total_connections_released}, max tracked: {self._max_tracked_connections}")

                    # SQLAlchemy typically reuses actual database connections while creating new Python wrapper objects
                    # So a high number of tracked objects doesn't necessarily mean connection leaks
                    if len(connection_ids) > self.config.pool_size * 0.8:
                        self.logger.info(f"Note: The number of tracked AsyncConnection objects ({len(connection_ids)}) can be much higher than the pool size ({self.config.pool_size}) because SQLAlchemy creates new wrapper objects while reusing the underlying connections.")

                        # Log detailed diagnostics about engine pool
                        if self._async_engine:
                            try:
                                pool = self._async_engine.pool
                                if hasattr(pool, "size") and hasattr(pool, "overflow"):
                                    self.logger.info(f"Actual pool stats - Size: {pool.size()}, Overflow: {pool.overflow()}")
                                    # There's no direct checked_out attribute or method, so we log what's available
                            except Exception as e:
                                self.logger.error(f"Error getting pool stats: {str(e)}")

                # Check for very long-lived connections
                current_time = time.time()
                for conn_id in connection_ids:
                    creation_time = self._connection_creation_times.get(conn_id)
                    if creation_time:
                        lifetime = current_time - creation_time
                        if lifetime > self._max_safe_connection_lifetime:
                            # This connection has been alive too long - might be a leak
                            self.logger.error(f"Connection {conn_id} has been alive for {lifetime:.2f}s, exceeding the maximum safe lifetime of {self._max_safe_connection_lifetime}s. Forcing cleanup.")
                            conn = self._active_connections.get(conn_id)
                            if conn:
                                try:
                                    # Attempt to close extremely long-lived connections
                                    task = asyncio.create_task(self._return_connection_to_pool(conn))
                                    self._background_tasks.add(task)
                                    task.add_done_callback(self._background_tasks.discard)
                                except Exception as e:
                                    self.logger.error(f"Error cleaning up long-lived connection: {str(e)}")

                        elif lifetime > self._long_lived_threshold:
                            self.logger.warning(f"Connection {conn_id} has been alive for {lifetime:.2f}s")

        except asyncio.CancelledError:
            self.logger.debug("Stale connection checker task cancelled")
        except Exception as e:
            self.logger.error(f"Error in stale connection check: {str(e)}")
