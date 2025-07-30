import functools
import time
from .exceptions import RagflowError, NetworkError


def retry_on_exception(retries=3, delay=1, exceptions=(NetworkError,)):
    """简单的重试装饰器。"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:
                    last_exc = exc
                    time.sleep(delay)
            raise last_exc
        return wrapper
    return decorator 