import contextlib
import functools
import sys


# Context manager for tracing
@contextlib.contextmanager
def tracer():
    def trace_calls(frame, event, arg):
        if event == "call":
            print(f"📞 Calling function: {frame.f_code.co_name}")
        elif event == "line":
            print(
                f"📌 Executing line {frame.f_lineno} in {frame.f_code.co_name}"
            )
        return trace_calls

    sys.settrace(trace_calls)  # Start tracing
    yield  # Run the code inside 'with' block
    sys.settrace(None)  # Stop tracing


# Decorator to trace a specific function
def trace_decorator(func):
    @functools.wraps(func)  # Preserve function metadata
    def wrapper(*args, **kwargs):
        with tracer():  # Start tracing only for this function
            return func(*args, **kwargs)

    return wrapper


# Example: Tracing only one function
@trace_decorator
def my_function():
    x = 10
    y = 20
    z = x + y
    print("Sum:", z)


# Run the function with automatic tracing
my_function()
