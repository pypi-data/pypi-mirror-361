"""
Retry logic utilities for AgentMeter SDK
"""

import time
import random
from functools import wraps
from typing import Callable, Type, Tuple
import httpx
from ..exceptions import AgentMeterError


def with_retry(
    max_retries: int = 3,
    backoff_factor: float = 1.0,
    retryable_exceptions: Tuple[Type[Exception], ...] = (httpx.RequestError, httpx.TimeoutException),
    retryable_status_codes: Tuple[int, ...] = (500, 502, 503, 504, 429)
):
    """Decorator for adding retry logic to functions."""
    
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except retryable_exceptions as e:
                    last_exception = e
                    if attempt == max_retries:
                        raise
                except AgentMeterError as e:
                    if hasattr(e, 'status_code') and e.status_code in retryable_status_codes:
                        last_exception = e
                        if attempt == max_retries:
                            raise
                    else:
                        raise
                
                # Calculate delay with jitter
                delay = backoff_factor * (2 ** attempt) + random.uniform(0, 1)
                time.sleep(delay)
            
            raise last_exception
        
        return wrapper
    return decorator 