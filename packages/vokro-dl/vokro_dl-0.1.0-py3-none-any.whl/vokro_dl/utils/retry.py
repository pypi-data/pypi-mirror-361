"""
Retry mechanism with exponential backoff for VokroDL.

This module provides robust retry functionality with configurable
backoff strategies and error handling.
"""

import asyncio
import logging
import random
import time
from typing import Any, Callable, Optional, Type, Union, Tuple
from functools import wraps

from ..core.config import RetryConfig
from ..core.exceptions import VokroDLError, NetworkError, RateLimitError


logger = logging.getLogger(__name__)


class RetryManager:
    """Manages retry logic with exponential backoff."""
    
    def __init__(self, config: RetryConfig):
        """
        Initialize retry manager.
        
        Args:
            config: Retry configuration
        """
        self.config = config
    
    async def execute(
        self,
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """
        Execute a function with retry logic.
        
        Args:
            func: Function to execute (can be sync or async)
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            Exception: Last exception if all retries failed
        """
        last_exception = None
        
        for attempt in range(self.config.max_retries + 1):
            try:
                # Execute function (handle both sync and async)
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                
                if attempt > 0:
                    logger.info(f"Operation succeeded after {attempt} retries")
                
                return result
                
            except Exception as e:
                last_exception = e
                
                # Don't retry on certain exceptions
                if not self._should_retry(e):
                    logger.debug(f"Not retrying due to exception type: {type(e).__name__}")
                    raise
                
                # Don't retry on last attempt
                if attempt >= self.config.max_retries:
                    logger.error(f"All {self.config.max_retries} retries failed")
                    raise
                
                # Calculate delay
                delay = self._calculate_delay(attempt, e)
                
                logger.warning(
                    f"Attempt {attempt + 1} failed: {str(e)}. "
                    f"Retrying in {delay:.2f} seconds..."
                )
                
                await asyncio.sleep(delay)
        
        # This should never be reached, but just in case
        if last_exception:
            raise last_exception
    
    def _should_retry(self, exception: Exception) -> bool:
        """
        Determine if an exception should trigger a retry.
        
        Args:
            exception: Exception that occurred
            
        Returns:
            True if should retry, False otherwise
        """
        # Always retry network errors
        if isinstance(exception, NetworkError):
            return True
        
        # Handle rate limiting with special logic
        if isinstance(exception, RateLimitError):
            return True
        
        # Retry on specific HTTP status codes
        if hasattr(exception, 'status_code'):
            # Retry on server errors and some client errors
            retry_codes = {500, 502, 503, 504, 408, 429}
            return exception.status_code in retry_codes
        
        # Retry on connection errors
        if isinstance(exception, (
            asyncio.TimeoutError,
            ConnectionError,
            OSError
        )):
            return True
        
        # Don't retry on VokroDL errors that aren't network-related
        if isinstance(exception, VokroDLError) and not isinstance(exception, NetworkError):
            return False
        
        # Default: retry on most exceptions
        return True
    
    def _calculate_delay(self, attempt: int, exception: Exception) -> float:
        """
        Calculate delay for next retry attempt.
        
        Args:
            attempt: Current attempt number (0-based)
            exception: Exception that triggered retry
            
        Returns:
            Delay in seconds
        """
        # Handle rate limiting specially
        if isinstance(exception, RateLimitError) and exception.retry_after:
            base_delay = exception.retry_after
        else:
            # Exponential backoff
            base_delay = self.config.initial_delay * (
                self.config.exponential_base ** attempt
            )
        
        # Cap at maximum delay
        delay = min(base_delay, self.config.max_delay)
        
        # Add jitter to avoid thundering herd
        if self.config.jitter:
            jitter_range = delay * 0.1  # 10% jitter
            jitter = random.uniform(-jitter_range, jitter_range)
            delay += jitter
        
        return max(0, delay)


def retry(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True
):
    """
    Decorator for adding retry logic to functions.
    
    Args:
        max_retries: Maximum number of retries
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        exponential_base: Exponential backoff base
        jitter: Add random jitter to delays
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            config = RetryConfig(
                max_retries=max_retries,
                initial_delay=initial_delay,
                max_delay=max_delay,
                exponential_base=exponential_base,
                jitter=jitter
            )
            retry_manager = RetryManager(config)
            return await retry_manager.execute(func, *args, **kwargs)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            config = RetryConfig(
                max_retries=max_retries,
                initial_delay=initial_delay,
                max_delay=max_delay,
                exponential_base=exponential_base,
                jitter=jitter
            )
            retry_manager = RetryManager(config)
            
            # For sync functions, we need to run in event loop
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            return loop.run_until_complete(
                retry_manager.execute(func, *args, **kwargs)
            )
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


class CircuitBreaker:
    """
    Circuit breaker pattern implementation for preventing cascading failures.
    
    This can be used to temporarily stop making requests to a failing service
    to give it time to recover.
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        expected_exception: Type[Exception] = Exception
    ):
        """
        Initialize circuit breaker.
        
        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Time to wait before trying again
            expected_exception: Exception type that triggers circuit breaker
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Call function through circuit breaker.
        
        Args:
            func: Function to call
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            Exception: If circuit is open or function fails
        """
        if self.state == "open":
            if self._should_attempt_reset():
                self.state = "half-open"
            else:
                raise NetworkError("Circuit breaker is open")
        
        try:
            # Execute function
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            # Success - reset circuit breaker
            self._on_success()
            return result
            
        except self.expected_exception as e:
            self._on_failure()
            raise
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if self.last_failure_time is None:
            return True
        
        return time.time() - self.last_failure_time >= self.recovery_timeout
    
    def _on_success(self):
        """Handle successful call."""
        self.failure_count = 0
        self.state = "closed"
    
    def _on_failure(self):
        """Handle failed call."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "open"
            logger.warning(
                f"Circuit breaker opened after {self.failure_count} failures"
            )
