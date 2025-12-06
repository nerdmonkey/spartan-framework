from app.helpers.tracer import (
    TracerService,
    capture_lambda_handler,
    capture_method,
    get_tracer,
    trace_function,
    trace_segment,
)


def test_tracer_helpers_are_exported():
    """Test that all tracer helpers are properly exported."""
    assert TracerService is not None
    assert capture_lambda_handler is not None
    assert capture_method is not None
    assert get_tracer is not None
    assert trace_function is not None
    assert trace_segment is not None


def test_get_tracer_returns_tracer_instance():
    """Test that get_tracer returns a tracer instance."""
    tracer = get_tracer()
    assert tracer is not None
    assert hasattr(tracer, "create_segment")
