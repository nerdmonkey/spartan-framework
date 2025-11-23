from contextlib import contextmanager

from contextlib import contextmanager
import sys
import types

# Prevent aws_xray_sdk from creating sockets during import in tests by
# inserting a lightweight fake module into sys.modules before importing
# any tracing modules that may import aws_xray_sdk.core at module load.
fake_core = types.ModuleType("aws_xray_sdk.core")
fake_core.xray_recorder = types.SimpleNamespace()
sys.modules["aws_xray_sdk.core"] = fake_core
sys.modules["aws_xray_sdk"] = types.ModuleType("aws_xray_sdk")
sys.modules["aws_xray_sdk"].core = fake_core

import pytest
from app.services.tracing.factory import TracerFactory
from app.services.tracing.local import LocalTracer
from app.services.tracing.cloud import CloudTracer
from app.services.tracing.gcloud import GCloudTracer

def test_env_override_selects_gcloud(monkeypatch):
    # Ensure env('TRACER_TYPE') returns 'gcloud'
    monkeypatch.setattr(
        "app.services.tracing.factory.env",
        lambda k, d=None: {"TRACER_TYPE": "gcloud", "APP_ENVIRONMENT": "production"}.get(k, d),
    )
    # Patch GCloudTracer to simulate GCP tracing available
    import app.services.tracing.gcloud as gcloud_mod
    monkeypatch.setattr(gcloud_mod, "GCP_TRACING_AVAILABLE", True)
    class FakeTrace:
        @staticmethod
        def TraceServiceClient(*args, **kwargs):
            return object()
    monkeypatch.setattr(gcloud_mod, "trace_v1", FakeTrace(), raising=False)
    tracer = TracerFactory.create_tracer(service_name="svc")
    assert isinstance(tracer, GCloudTracer)

def test_param_override_selects_local(monkeypatch):
    # Even if environment indicates cloud, explicit parameter should win
    monkeypatch.setattr(
        "app.services.tracing.factory.env",
        lambda k, d=None: {"TRACER_TYPE": "gcloud", "APP_ENVIRONMENT": "production"}.get(k, d),
    )
    tracer = TracerFactory.create_tracer(service_name="svc", tracer_type="local")
    assert isinstance(tracer, LocalTracer)

def test_invalid_override_raises(monkeypatch):
    monkeypatch.setattr(
        "app.services.tracing.factory.env",
        lambda k, d=None: {"APP_ENVIRONMENT": "production"}.get(k, d),
    )
    with pytest.raises(ValueError):
        TracerFactory.create_tracer(service_name="svc", tracer_type="unsupported-tracer")

def test_gcloud_tracer_basic_behaviour(monkeypatch):
    """GCloudTracer should construct when trace_v1 is available and its wrappers should call through."""
    mod = __import__("app.services.tracing.gcloud", fromlist=["*"])

    # Make trace available
    monkeypatch.setattr(mod, "GCP_TRACING_AVAILABLE", True)
    monkeypatch.setattr(mod, "trace_v1", __import__("types").SimpleNamespace(TraceServiceClient=lambda: __import__("types").SimpleNamespace()), raising=False)

    from app.services.tracing.gcloud import GCloudTracer

    gw = GCloudTracer("svc")

    # capture_lambda_handler should return a wrapper that calls the original
    called = {}

    def handler(event, context):
        called['ok'] = True
        return "result"

    wrapped = gw.capture_lambda_handler(handler)
    res = wrapped({}, {})
    assert res == "result"
    assert called.get('ok') is True

    # create_segment should be usable as a context manager
    with gw.create_segment("seg"):
        x = 1
    assert x == 1


def test_tracerservice_delegation(monkeypatch):
    """TracerService helpers should delegate to the underlying tracer instance."""
    from app.services.tracer import TracerService, trace_function, trace_segment, capture_lambda_handler, capture_method

    # Create a fake tracer that records calls
    class FakeTracer:
        def __init__(self):
            self.segments = []

        @contextmanager
        def create_segment(self, name, metadata=None):
            self.segments.append(("enter", name, metadata))
            try:
                yield
            finally:
                self.segments.append(("exit", name, metadata))

        def capture_lambda_handler(self, handler):
            def wrapper(event, context):
                return handler(event, context)

            return wrapper

        def capture_method(self, method):
            def wrapper(*args, **kwargs):
                return method(*args, **kwargs)

            return wrapper

    fake = FakeTracer()

    # Monkeypatch TracerService.get_tracer to return our fake tracer
    monkeypatch.setattr(TracerService, "get_tracer", staticmethod(lambda: fake))

    # Test trace_function decorator
    @trace_function(name="myseg")
    def f():
        return 42

    assert f() == 42
    # Should have entered and exited the segment
    assert ("enter", "myseg", None) in fake.segments
    assert ("exit", "myseg", None) in fake.segments

    # Test trace_segment context manager
    with trace_segment("outer", {"a": 1}):
        pass
    assert ("enter", "outer", {"a": 1}) in fake.segments
    assert ("exit", "outer", {"a": 1}) in fake.segments

    # Test capture_lambda_handler and capture_method delegate
    def handler(e, c):
        return "ok"

    deco = capture_lambda_handler(handler)
    # capture_lambda_handler returns a callable that wraps the handler
    assert callable(deco)

    class C:
        def m(self):
            return "m"

    cm = capture_method(C.m)
    assert callable(cm)
