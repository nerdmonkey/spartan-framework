from contextlib import contextmanager
from functools import wraps
from typing import Any, Dict, Optional

from .factory import get_tracer


def trace_function(name: Optional[str] = None):
    """Decorator for tracing functions."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            tracer = get_tracer()
            segment_name = name or func.__name__
            with tracer.create_segment(segment_name):
                return func(*args, **kwargs)

        return wrapper

    return decorator


@contextmanager
def trace_segment(name: str, metadata: Optional[Dict[str, Any]] = None):
    """Context manager for creating trace segments."""
    tracer = get_tracer()
    with tracer.create_segment(name, metadata):
        yield


def capture_lambda_handler(handler):
    """Decorator for tracing Lambda handlers."""
    tracer = get_tracer()
    return tracer.capture_lambda_handler(handler)


def capture_method(method):
    """Decorator for tracing class methods."""
    tracer = get_tracer()
    return tracer.capture_method(method)


__all__ = [
    "trace_function",
    "trace_segment",
    "capture_lambda_handler",
    "capture_method",
    "get_tracer",
]
