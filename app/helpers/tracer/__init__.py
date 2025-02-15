from typing import Optional, Dict, Any
from contextlib import contextmanager
from functools import wraps
from .factory import get_tracer

def trace_function(name: Optional[str] = None):
    """Decorator for tracing functions"""
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
    """Context manager for creating trace segments"""
    tracer = get_tracer()
    with tracer.create_segment(name, metadata):
        yield
