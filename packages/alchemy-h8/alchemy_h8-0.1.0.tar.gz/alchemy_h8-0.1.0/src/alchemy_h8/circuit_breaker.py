"""
Circuit breaker implementation for database connections.
Prevents overwhelming the database with requests when it's having issues.
"""
import time
import enum
import logging
from typing import Optional

import structlog

logger = structlog.get_logger(__name__)


class CircuitBreakerState(enum.Enum):
    """States for the circuit breaker."""
    CLOSED = "closed"  # Circuit is closed, allowing connections
    OPEN = "open"  # Circuit is open, rejecting connections
    HALF_OPEN = "half_open"  # Circuit is allowing a test connection


class CircuitBreaker:
    """
    Implementation of the circuit breaker pattern.
    
    When failures exceed a threshold, the circuit opens and connections are rejected
    for a period of time. After that period, a single test connection is allowed.
    If it succeeds, the circuit closes again; if it fails, the circuit remains open.
    """
    class CircuitBreakerOpenError(Exception):
        """Exception raised when the circuit is open."""
        pass

    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 30):
        """
        Initialize circuit breaker.
        
        Args:
            failure_threshold: Number of consecutive failures before opening circuit
            recovery_timeout: Seconds to wait before allowing test connection
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self._state = CircuitBreakerState.CLOSED
        self._failure_count = 0
        self._next_attempt_time: Optional[float] = None
        
    @property
    def state(self) -> CircuitBreakerState:
        """Get current state of the circuit breaker."""
        # If circuit is open but recovery timeout has passed, move to half-open
        if (self._state == CircuitBreakerState.OPEN and 
            self._next_attempt_time is not None and 
            time.time() >= self._next_attempt_time):
            self._state = CircuitBreakerState.HALF_OPEN
            logger.info("Circuit breaker state changed from OPEN to HALF_OPEN")
            
        return self._state
        
    @property
    def next_attempt_time(self) -> Optional[float]:
        """Get timestamp when the next connection attempt will be allowed."""
        return self._next_attempt_time
        
    def record_success(self) -> None:
        """Record a successful operation, potentially closing the circuit."""
        if self._state == CircuitBreakerState.HALF_OPEN:
            self._state = CircuitBreakerState.CLOSED
            self._failure_count = 0
            self._next_attempt_time = None
            logger.info("Circuit breaker state changed from HALF_OPEN to CLOSED")
        elif self._state == CircuitBreakerState.CLOSED:
            self._failure_count = 0
            
    def record_failure(self) -> None:
        """
        Record a failed operation, potentially opening the circuit.
        
        If in half-open state, immediately opens the circuit.
        If in closed state, increments failure counter and opens if threshold reached.
        """
        if self._state == CircuitBreakerState.HALF_OPEN:
            self._state = CircuitBreakerState.OPEN
            self._next_attempt_time = time.time() + self.recovery_timeout
            logger.warning("Circuit breaker test connection failed, returning to OPEN state")
        elif self._state == CircuitBreakerState.CLOSED:
            self._failure_count += 1
            if self._failure_count >= self.failure_threshold:
                self._state = CircuitBreakerState.OPEN
                self._next_attempt_time = time.time() + self.recovery_timeout
                logger.warning(
                    f"Circuit breaker threshold reached ({self._failure_count} failures), "
                    f"opening circuit for {self.recovery_timeout} seconds"
                )
