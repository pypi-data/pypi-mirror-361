"""
Rate limiter implementation for database connections.
Allows controlling the frequency and concurrency of database operations.
"""
import time
import logging
import asyncio
from enum import Enum
from typing import Optional, Dict, Any, Callable, Awaitable, List, Coroutine

import structlog

logger = structlog.get_logger(__name__)


class RateLimiterState(Enum):
    """Possible states of the rate limiter."""
    INACTIVE = "inactive"  # Not limiting - all requests pass through
    ACTIVE = "active"      # Actively limiting requests


class RateLimiterStrategy(Enum):
    """Different rate limiting strategies."""
    TOKEN_BUCKET = "token_bucket"  # Classic token bucket algorithm
    FIXED_WINDOW = "fixed_window"  # Fixed window counter
    LEAKY_BUCKET = "leaky_bucket"  # Leaky bucket algorithm


class RateLimiterError(Exception):
    """Exception raised when rate limit is exceeded."""
    pass


class RateLimiter:
    """
    Rate limiter implementation that controls request rate to the database.
    
    This helps protect the database from being overwhelmed with too many
    concurrent requests in a short time period. Different from circuit breaker,
    which protects against failures, this protects against overwhelming load.
    """
    
    def __init__(
        self,
        max_requests: int = 100,
        time_window: float = 1.0,  # in seconds
        strategy: RateLimiterStrategy = RateLimiterStrategy.TOKEN_BUCKET,
        max_delay: float = 2.0,     # max time to wait before failing
        enabled: bool = True
    ):
        """
        Initialize rate limiter.
        
        Args:
            max_requests: Maximum number of requests allowed in the time window
            time_window: Time window in seconds
            strategy: Rate limiting algorithm to use
            max_delay: Maximum delay in seconds before failing a request
            enabled: Whether rate limiting is enabled
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.strategy = strategy
        self.max_delay = max_delay
        self._enabled = enabled
        self._state = RateLimiterState.INACTIVE if not enabled else RateLimiterState.ACTIVE
        
        # Strategy-specific attributes
        self._tokens = max_requests  # For token bucket
        self._last_refill_time = time.time()
        self._request_times: List[float] = []     # For fixed window
        self._request_lock = asyncio.Lock()
        
        logger.info(f"Rate limiter initialized with {strategy.value} strategy, "
                   f"max {max_requests} requests per {time_window}s window, "
                   f"enabled: {enabled}")
    
    @property
    def state(self) -> RateLimiterState:
        """Get current state of the rate limiter."""
        return self._state
    
    @property
    def enabled(self) -> bool:
        """Check if rate limiter is enabled."""
        return self._enabled
    
    def enable(self) -> None:
        """Enable rate limiting."""
        self._enabled = True
        self._state = RateLimiterState.ACTIVE
        logger.info("Rate limiter enabled")
    
    def disable(self) -> None:
        """Disable rate limiting."""
        self._enabled = False
        self._state = RateLimiterState.INACTIVE
        logger.info("Rate limiter disabled")
    
    async def _refill_tokens(self) -> None:
        """Refill tokens for token bucket algorithm based on elapsed time."""
        now = time.time()
        elapsed = now - self._last_refill_time
        
        # Calculate tokens to add based on elapsed time
        new_tokens = int(elapsed * (self.max_requests / self.time_window))
        if new_tokens > 0:
            self._tokens = min(self._tokens + new_tokens, self.max_requests)
            self._last_refill_time = now
    
    async def _clean_request_window(self) -> None:
        """Remove outdated requests from the fixed window."""
        now = time.time()
        cutoff = now - self.time_window
        self._request_times = [t for t in self._request_times if t > cutoff]
    
    async def check_rate_limit(self) -> bool | None:
        """
        Check if the request can proceed under current rate limits.
        Returns True if request can proceed, False otherwise.
        """
        if not self._enabled:
            return True
            
        async with self._request_lock:
            if self.strategy == RateLimiterStrategy.TOKEN_BUCKET:
                await self._refill_tokens()
                if self._tokens > 0:
                    self._tokens -= 1
                    return True
                else:
                    return False
                    
            elif self.strategy == RateLimiterStrategy.FIXED_WINDOW:
                await self._clean_request_window()
                if len(self._request_times) < self.max_requests:
                    self._request_times.append(time.time())
                    return True
                else:
                    return False
                    
            elif self.strategy == RateLimiterStrategy.LEAKY_BUCKET:
                # Simplified leaky bucket implementation
                await self._clean_request_window()
                current_rate = len(self._request_times) / self.time_window
                target_rate = self.max_requests / self.time_window
                
                if current_rate < target_rate:
                    self._request_times.append(time.time())
                    return True
                else:
                    return False
            # This code is technically unreachable since we cover all enum values above,
            # but mypy doesn't recognize this, so keeping it as a safeguard
            logger.warning(f"Unknown rate limiting strategy: {self.strategy}") # type: ignore[unreachable]
            return None
    
    async def attempt_acquire(self) -> bool:
        """
        Try to acquire permission to proceed under rate limit.
        Will wait for a short time if rate limit is hit temporarily.
        
        Returns:
            True if permission granted, False if rate limit exceeded.
        """
        if not self._enabled:
            return True
            
        # Quick check first
        can_proceed = await self.check_rate_limit()
        if can_proceed:
            return True
            
        # If we can't proceed immediately, try waiting for a bit
        start_time = time.time()
        backoff = 0.01  # Start with 10ms
        
        while (time.time() - start_time) < self.max_delay:
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 0.5)  # Exponential backoff up to 500ms
            
            can_proceed = await self.check_rate_limit()
            if can_proceed:
                return True
        
        # If we reach here, we've exceeded the maximum delay
        return False
    
    async def execute_with_rate_limit(
        self, 
        func: Callable[..., Awaitable[Any]],
        *args: Any,
        **kwargs: Any
    ) -> Any:
        """
        Execute a function with rate limiting applied.
        
        Args:
            func: Async function to execute
            *args: Arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            Result from the function
            
        Raises:
            RateLimiterError: When rate limit is exceeded
        """
        if not self._enabled:
            return await func(*args, **kwargs)
        
        # Try to acquire permission
        acquired = await self.attempt_acquire()
        if not acquired:
            logger.warning("Rate limit exceeded, rejecting request")
            raise RateLimiterError("Database rate limit exceeded, try again later")
            
        # Execute the function if we have permission
        return await func(*args, **kwargs)
