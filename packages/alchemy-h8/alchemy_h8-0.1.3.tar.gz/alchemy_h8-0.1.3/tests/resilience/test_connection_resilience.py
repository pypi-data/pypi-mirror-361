"""
Integration tests for database connection resilience.
These tests verify the library's ability to handle real database failures
and recover gracefully.
"""

import asyncio
import os
from typing import AsyncGenerator, List

import asyncpg
import pytest
import pytest_asyncio
from sqlalchemy import Column, Integer, MetaData, String, Table, text
from sqlalchemy.exc import OperationalError

from src.alchemy_h8.circuit_breaker import CircuitBreakerState
from src.alchemy_h8.config import DBConnectionConfig
from src.alchemy_h8.connection import DBConnectionHandler
from src.alchemy_h8.rate_limiter import (
    RateLimiterError,
    RateLimiterStrategy,
)

# Use environment variables or defaults for test database
DB_HOST = os.getenv("TEST_DB_HOST", "localhost")
DB_PORT = int(os.getenv("TEST_DB_PORT", "5432"))
DB_USER = os.getenv("TEST_DB_USER", "postgres")
DB_PASS = os.getenv("TEST_DB_PASS", "postgres")
DB_NAME = os.getenv("TEST_DB_NAME", "test_db")


@pytest_asyncio.fixture
async def test_table(
    db_connection_handler: DBConnectionHandler,
) -> AsyncGenerator[Table, None]:
    """Create a test table for the duration of the test."""
    metadata = MetaData()
    test_table = Table(
        "resilience_test",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("data", String(50)),
    )

    # Use DBConnectionHandler's connection method instead of direct engine access
    async with db_connection_handler.get_async_connection() as conn:
        # Execute each SQL statement separately to avoid 'multiple commands' error
        # Drop table if exists
        await conn.execute(text("DROP TABLE IF EXISTS resilience_test"))
        await conn.commit()

        # Create table
        await conn.execute(
            text(
                """
            CREATE TABLE resilience_test (
                id SERIAL PRIMARY KEY,
                data VARCHAR(50)
            )
        """
            )
        )
        await conn.commit()

        # Ensure table is empty
        await conn.execute(text("TRUNCATE TABLE resilience_test"))
        await conn.commit()

    try:
        yield test_table
    finally:
        # Clean up after test with explicit commit
        async with db_connection_handler.get_async_connection() as conn:
            await conn.execute(text("DROP TABLE IF EXISTS resilience_test"))
            await conn.commit()  # Explicitly commit the drop


@pytest_asyncio.fixture
async def db_connection_handler() -> AsyncGenerator[DBConnectionHandler, None]:
    """Create a database connection handler for testing."""
    config = DBConnectionConfig(
        host=DB_HOST,
        port=DB_PORT,
        username=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        # Smaller pool for testing
        pool_size=2,
        max_overflow=3,
        pool_timeout=5,
        # Enable circuit breaker with lower thresholds for testing
        use_circuit_breaker=True,
        circuit_breaker_threshold=3,
        circuit_breaker_recovery_timeout=2,
        # Enable rate limiter with strict limits for testing
        use_rate_limiter=True,
        rate_limit_max_requests=10,
        rate_limit_time_window=1.0,
        rate_limit_strategy=RateLimiterStrategy.TOKEN_BUCKET,
        rate_limit_max_delay=0.5,
        # Enable logging for tests
        echo=True,
    )

    handler = DBConnectionHandler(config)
    await handler.initialize()

    try:
        yield handler
    finally:
        await handler.dispose_gracefully()


@pytest.mark.asyncio
async def test_basic_connection(db_connection_handler: DBConnectionHandler) -> None:
    """Test basic database connection functionality."""
    # Get connection from pool
    async with db_connection_handler.get_async_connection() as conn:
        # Execute a simple query
        result = await conn.execute(text("SELECT 1 as value"))
        row = result.fetchone()

        assert row is not None
        assert row[0] == 1


@pytest.mark.asyncio
async def test_basic_crud_operations(db_connection_handler: DBConnectionHandler, test_table: Table) -> None:
    """Test basic CRUD operations."""
    # Use autocommit for this test to ensure changes persist
    async with db_connection_handler.get_async_connection() as conn:
        # Insert
        result = await conn.execute(
            text("INSERT INTO resilience_test (data) VALUES (:data) RETURNING id"),
            {"data": "test_data"},
        )
        row = result.fetchone()
        insert_id = row[0]

        # Select
        result = await conn.execute(text("SELECT * FROM resilience_test WHERE id = :id"), {"id": insert_id})
        row = result.fetchone()

        assert row is not None
        assert row[0] == insert_id
        assert row[1] == "test_data"

        # Update
        await conn.execute(
            text("UPDATE resilience_test SET data = :data WHERE id = :id"),
            {"id": insert_id, "data": "updated_data"},
        )

        # Verify update
        result = await conn.execute(text("SELECT data FROM resilience_test WHERE id = :id"), {"id": insert_id})
        row = result.fetchone()

        assert row is not None
        assert row[0] == "updated_data"

        # Delete
        await conn.execute(text("DELETE FROM resilience_test WHERE id = :id"), {"id": insert_id})

        # Verify deletion
        result = await conn.execute(
            text("SELECT COUNT(*) FROM resilience_test WHERE id = :id"),
            {"id": insert_id},
        )
        row = result.fetchone()

        assert row is not None
        assert row[0] == 0


@pytest.mark.asyncio
async def test_connection_pool_limits(
    db_connection_handler: DBConnectionHandler,
) -> None:
    """Test connection pool enforces limits correctly."""
    # The pool has size=2, max_overflow=3, so we should be able to get 5 connections
    # before hitting the limit
    connections = []

    try:
        # Get connections until pool is exhausted
        for i in range(5):
            conn = await db_connection_handler._async_engine.connect()
            connections.append(conn)

        # The next connection should time out
        with pytest.raises((asyncio.TimeoutError, asyncpg.exceptions.TooManyConnectionsError)):
            await asyncio.wait_for(db_connection_handler._async_engine.connect(), timeout=2)
    finally:
        # Close all connections
        for conn in connections:
            await conn.close()


@pytest.mark.asyncio
async def test_rate_limiter(db_connection_handler: DBConnectionHandler, test_table: Table) -> None:
    """Test rate limiter prevents exceeding request limits."""
    # Set a very strict rate limit for testing
    db_connection_handler._rate_limiter.max_requests = 3
    db_connection_handler._rate_limiter.time_window = 1.0
    db_connection_handler._rate_limiter.max_delay = 0.0  # No delay, immediate failure

    # Get direct access to the rate limiter for more predictable behavior in tests
    rate_limiter = db_connection_handler._rate_limiter

    # Force reset token bucket to known state
    if hasattr(rate_limiter, "_tokens"):  # For token bucket strategy
        rate_limiter._tokens = rate_limiter.max_requests
    if hasattr(rate_limiter, "_last_refill"):
        rate_limiter._last_refill = time.time()

    # Execute queries up to the limit
    async def execute_query():
        async with db_connection_handler.get_async_connection() as conn:
            result = await conn.execute(text("SELECT 1"))
            value = result.scalar()
            return value

    # Consume all tokens
    results = []
    for i in range(3):
        try:
            value = await execute_query()
            results.append(value)
        except Exception as e:
            print(f"Unexpected error during token consumption: {str(e)}")

    assert all(result == 1 for result in results), "All queries should succeed"
    assert len(results) == 3, "Should execute exactly 3 successful queries"

    # The next query should be rate limited - try up to 3 times to handle race conditions
    rate_limited = False
    for attempt in range(3):
        try:
            await execute_query()
            # Small wait between attempts if rate limit not yet triggered
            await asyncio.sleep(0.1)
        except RateLimiterError:
            rate_limited = True
            break
        except Exception as e:
            print(f"Unexpected error: {str(e)}")

    assert rate_limited, "Should have triggered rate limiter"

    # Wait for rate limit to reset
    await asyncio.sleep(1.1)

    # Should be able to execute again
    try:
        value = await execute_query()
        assert value == 1, "Should be able to execute query after rate limit reset"
    except Exception as e:
        assert False, f"Should not raise exception after waiting: {str(e)}"


@pytest.mark.asyncio
async def test_circuit_breaker(db_connection_handler: DBConnectionHandler) -> None:
    """Test circuit breaker opens after repeated failures."""
    # Make the circuit breaker record failures
    for _ in range(db_connection_handler._circuit_breaker.failure_threshold):
        db_connection_handler._circuit_breaker.record_failure()

    # Verify circuit breaker is open
    assert db_connection_handler._circuit_breaker.state == CircuitBreakerState.OPEN

    # Try to get a connection, should be rejected
    with pytest.raises(Exception) as exc_info:
        async with db_connection_handler.get_async_connection() as conn:
            pass

    # Wait for circuit recovery timeout
    await asyncio.sleep(db_connection_handler._circuit_breaker.recovery_timeout + 0.1)

    # Circuit should now be half-open
    assert db_connection_handler._circuit_breaker.state == CircuitBreakerState.HALF_OPEN

    # Make a successful connection to close the circuit
    async with db_connection_handler.get_async_connection() as conn:
        await conn.execute(text("SELECT 1"))

    # Circuit should now be closed
    assert db_connection_handler._circuit_breaker.state == CircuitBreakerState.CLOSED


@pytest.mark.asyncio
async def test_retry_logic(db_connection_handler: DBConnectionHandler) -> None:
    """Test retry logic works with connection failures."""
    import sqlalchemy.ext.asyncio

    # Track the number of connection attempts
    failure_count = 0

    # Store the original connect method
    original_connect = sqlalchemy.ext.asyncio.AsyncEngine.connect

    # Define our mock async connect method
    async def mock_connect(self, *args, **kwargs):
        nonlocal failure_count
        failure_count += 1

        if failure_count <= 2:
            # Simulate a connection failure with an error message that will be recognized as transient
            pg_error = asyncpg.exceptions.ConnectionDoesNotExistError("could not connect to server: Connection refused")
            raise OperationalError("Connection failed: connection refused", None, pg_error)

        # After two failures, use the original method to get a real connection
        return await original_connect(self, *args, **kwargs)

    # Configure retry settings for faster test execution
    original_max_retries = db_connection_handler._max_retries
    original_base_delay = db_connection_handler._base_retry_delay

    # Set faster retry configuration for testing
    db_connection_handler._max_retries = 3
    db_connection_handler._base_retry_delay = 0.1

    try:
        # Apply the monkey patch to the SQLAlchemy AsyncEngine.connect method
        sqlalchemy.ext.asyncio.AsyncEngine.connect = mock_connect

        # This should succeed after retries
        async with db_connection_handler.get_async_connection() as conn:
            # Verify we got a valid connection
            result = await conn.execute(text("SELECT 1"))
            value = result.scalar()
            assert value == 1

            # Verify we had the expected number of connection attempts
            assert failure_count == 3  # Two failures and one success
    finally:
        # Restore the original method to avoid affecting other tests
        sqlalchemy.ext.asyncio.AsyncEngine.connect = original_connect

        # Restore original retry settings
        db_connection_handler._max_retries = original_max_retries
        db_connection_handler._base_retry_delay = original_base_delay


@pytest.mark.asyncio
async def test_connection_timeout(db_connection_handler: DBConnectionHandler) -> None:
    """Test connections timeout after configured timeout period."""
    # Create a config with a very short pool_timeout
    config = DBConnectionConfig(
        host=DB_HOST,
        port=DB_PORT,
        username=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        pool_size=1,  # Minimum pool size for testing
        pool_timeout=0.1,  # Very short timeout
        max_overflow=0,  # No overflow allowed - this is critical for testing timeouts
        use_circuit_breaker=False,  # Disable circuit breaker to ensure we test pool timeout
        use_rate_limiter=False,  # Disable rate limiter
    )

    handler = DBConnectionHandler(config)
    try:
        await handler.initialize()

        # Get and hold one connection to fill the pool completely
        async with handler.get_async_connection() as conn:
            result = await conn.execute(text("SELECT 1"))
            assert result.scalar() == 1

            # The pool is now full, next connection attempt should timeout
            # since we're still holding the one connection within this context
            with pytest.raises(Exception) as excinfo:
                async with asyncio.timeout(1.0):  # Add a timeout to avoid hanging
                    async with handler.get_async_connection() as conn2:
                        await conn2.execute(text("SELECT 1"))

            # Check if we got a timeout or pool full error
            error_text = str(excinfo.value).lower()
            assert any(text in error_text for text in ["timeout", "connection", "pool"])
    finally:
        # Make sure to clean up
        await handler.dispose_gracefully()


@pytest.mark.asyncio
async def test_concurrent_connections(db_connection_handler: DBConnectionHandler, test_table: Table) -> None:
    """Test multiple concurrent connections work correctly."""
    # First ensure table is empty
    async with db_connection_handler.get_async_connection() as conn:
        await conn.execute(text("TRUNCATE TABLE resilience_test"))
        await conn.commit()

        # Verify it's empty
        result = await conn.execute(text("SELECT COUNT(*) FROM resilience_test"))
        count = result.scalar()
        assert count == 0, f"Table should be empty before test, has {count} rows"

    async def worker(worker_id: int) -> List[int]:
        """Worker that inserts data and returns IDs."""
        ids = []
        async with db_connection_handler.get_async_connection() as conn:
            for i in range(5):
                result = await conn.execute(
                    text("INSERT INTO resilience_test (data) VALUES (:data) RETURNING id"),
                    {"data": f"worker_{worker_id}_item_{i}"},
                )
                row_id = result.scalar()
                ids.append(row_id)
            await conn.commit()  # Ensure data is committed
        return ids

    # Run 3 workers concurrently
    worker_tasks = [asyncio.create_task(worker(i)) for i in range(3)]
    worker_results = await asyncio.gather(*worker_tasks)

    # Flatten results
    all_ids = [id for worker_ids in worker_results for id in worker_ids]

    # Verify we have the expected number of results
    async with db_connection_handler.get_async_connection() as conn:
        result = await conn.execute(text("SELECT COUNT(*) FROM resilience_test"))
        count = result.scalar()
        assert count == 15, f"Expected 15 rows (3 workers × 5 items), got {count}"
        assert len(all_ids) == 15, f"Expected 15 IDs, got {len(all_ids)}"

        # Verify data integrity - each ID should be unique
        assert len(set(all_ids)) == 15, f"Not all IDs are unique: {all_ids}"
