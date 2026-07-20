import sys
import types
from contextlib import contextmanager

import pytest

from app.services.tracing.factory import TracerFactory
from app.services.tracing.gcp import GCPTracer
from app.services.tracing.local import LocalTracer


# Prevent aws_xray_sdk from creating sockets during import in tests by
# inserting a lightweight fake module into sys.modules before importing
# any tracing modules that may import aws_xray_sdk.core at module load.
fake_core = types.ModuleType("aws_xray_sdk.core")
fake_core.xray_recorder = types.SimpleNamespace()
sys.modules["aws_xray_sdk.core"] = fake_core
sys.modules["aws_xray_sdk"] = types.ModuleType("aws_xray_sdk")
sys.modules["aws_xray_sdk"].core = fake_core


def test_env_override_selects_gcp(monkeypatch):
    # Ensure env('TRACER_TYPE') returns 'gcp'
    monkeypatch.setattr(
        "app.services.tracing.factory.env",
        lambda k, d=None: {
            "TRACER_TYPE": "gcp",
            "APP_ENVIRONMENT": "production",
        }.get(k, d),
    )
    # Patch GCPTracer to simulate GCP tracing available
    import app.services.tracing.gcp as gcp_mod

    monkeypatch.setattr(gcp_mod, "GCP_TRACING_AVAILABLE", True)

    class FakeTrace:
        @staticmethod
        def TraceServiceClient(*args, **kwargs):
            return object()

    monkeypatch.setattr(gcp_mod, "trace_v1", FakeTrace(), raising=False)
    tracer = TracerFactory.create_tracer(service_name="svc")
    assert isinstance(tracer, GCPTracer)


def test_param_override_selects_local(monkeypatch):
    # Even if environment indicates cloud, explicit parameter should win
    monkeypatch.setattr(
        "app.services.tracing.factory.env",
        lambda k, d=None: {
            "TRACER_TYPE": "gcp",
            "APP_ENVIRONMENT": "production",
        }.get(k, d),
    )
    tracer = TracerFactory.create_tracer(service_name="svc", tracer_type="local")
    assert isinstance(tracer, LocalTracer)


def test_invalid_override_raises(monkeypatch):
    monkeypatch.setattr(
        "app.services.tracing.factory.env",
        lambda k, d=None: {"APP_ENVIRONMENT": "production"}.get(k, d),
    )
    with pytest.raises(ValueError):
        TracerFactory.create_tracer(
            service_name="svc", tracer_type="unsupported-tracer"
        )


def test_gcp_tracer_basic_behaviour(monkeypatch):
    """GCPTracer should construct when trace_v1 is available and its wrappers should call through."""
    mod = __import__("app.services.tracing.gcp", fromlist=["*"])

    # Make trace available
    monkeypatch.setattr(mod, "GCP_TRACING_AVAILABLE", True)
    monkeypatch.setattr(
        mod,
        "trace_v1",
        __import__("types").SimpleNamespace(
            TraceServiceClient=lambda: __import__("types").SimpleNamespace()
        ),
        raising=False,
    )

    from app.services.tracing.gcp import GCPTracer

    gw = GCPTracer("svc")

    # capture_lambda_handler should return a wrapper that calls the original
    called = {}

    def handler(event, context):
        called["ok"] = True
        return "result"

    wrapped = gw.capture_lambda_handler(handler)
    res = wrapped({}, {})
    assert res == "result"
    assert called.get("ok") is True

    # create_segment should be usable as a context manager
    with gw.create_segment("seg"):
        x = 1
    assert x == 1


def _build_fake_tracer():
    from app.services.tracer import (
        TracerService,
        capture_lambda_handler,
        capture_method,
        trace_function,
        trace_segment,
    )

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

    return (
        FakeTracer(),
        TracerService,
        capture_lambda_handler,
        capture_method,
        trace_function,
        trace_segment,
    )


def test_tracerservice_trace_function(monkeypatch):
    fake, TracerService, _, _, trace_function, _ = _build_fake_tracer()
    monkeypatch.setattr(TracerService, "get_tracer", staticmethod(lambda: fake))

    @trace_function(name="myseg")
    def f():
        return 42

    assert f() == 42
    assert ("enter", "myseg", None) in fake.segments
    assert ("exit", "myseg", None) in fake.segments


def test_tracerservice_trace_segment(monkeypatch):
    fake, TracerService, _, _, _, trace_segment = _build_fake_tracer()
    monkeypatch.setattr(TracerService, "get_tracer", staticmethod(lambda: fake))

    with trace_segment("outer", {"a": 1}):
        pass
    assert ("enter", "outer", {"a": 1}) in fake.segments
    assert ("exit", "outer", {"a": 1}) in fake.segments


def test_tracerservice_capture_helpers(monkeypatch):
    fake, TracerService, capture_lambda_handler, capture_method, _, _ = (
        _build_fake_tracer()
    )
    monkeypatch.setattr(TracerService, "get_tracer", staticmethod(lambda: fake))

    def handler(e, c):
        return "ok"

    deco = capture_lambda_handler(handler)
    assert callable(deco)

    class C:
        def m(self):
            return "m"

    cm = capture_method(C.m)
    assert callable(cm)
