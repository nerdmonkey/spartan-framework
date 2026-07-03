import importlib
from types import SimpleNamespace


def test_tracer_factory_selects_gcp_when_gcp_env(monkeypatch):
    # Patch env to simulate GCP environment and non-local app env
    monkeypatch.setattr(
        "app.helpers.environment.env",
        lambda k=None, d=None: {
            "APP_ENVIRONMENT": "prod",
            "GOOGLE_CLOUD_PROJECT": "myproj",
            "APP_NAME": "svc",
        }.get(k, d),
    )

    # Ensure gcp tracer thinks the GCP tracing client is available
    # Prevent aws_xray_sdk from performing network/socket operations during import
    import sys

    fake_xray = SimpleNamespace(
        xray_recorder=SimpleNamespace(
            begin_segment=lambda *a, **k: None,
            end_segment=lambda *a, **k: None,
            begin_subsegment=lambda *a, **k: None,
            end_subsegment=lambda *a, **k: None,
            put_annotation=lambda *a, **k: None,
        )
    )
    monkeypatch.setitem(sys.modules, "aws_xray_sdk", SimpleNamespace())
    monkeypatch.setitem(sys.modules, "aws_xray_sdk.core", fake_xray)

    mod_gcp = importlib.import_module("app.services.tracing.gcp")
    monkeypatch.setattr(mod_gcp, "GCP_TRACING_AVAILABLE", True)
    # Provide a fake trace_v1 with TraceServiceClient constructor (module may not define trace_v1)
    monkeypatch.setattr(
        mod_gcp,
        "trace_v1",
        SimpleNamespace(TraceServiceClient=lambda: SimpleNamespace()),
        raising=False,
    )

    # Reload factory so it picks up the patched env
    factory = importlib.reload(importlib.import_module("app.services.tracing.factory"))

    tracer = factory.get_tracer("svc")
    # Class name check (avoid importing GCPTracer directly to keep test light)
    assert tracer.__class__.__name__ == "GCPTracer"


def test_tracer_factory_returns_local_when_local_env(monkeypatch):
    monkeypatch.setattr(
        "app.helpers.environment.env",
        lambda k=None, d=None: {"APP_ENVIRONMENT": "local", "APP_NAME": "svc"}.get(
            k, d
        ),
    )
    # Prevent aws_xray_sdk side-effects during import
    import sys

    fake_xray = SimpleNamespace(
        xray_recorder=SimpleNamespace(
            begin_segment=lambda *a, **k: None,
            end_segment=lambda *a, **k: None,
            begin_subsegment=lambda *a, **k: None,
            end_subsegment=lambda *a, **k: None,
            put_annotation=lambda *a, **k: None,
        )
    )
    monkeypatch.setitem(sys.modules, "aws_xray_sdk", SimpleNamespace())
    monkeypatch.setitem(sys.modules, "aws_xray_sdk.core", fake_xray)

    factory = importlib.reload(importlib.import_module("app.services.tracing.factory"))
    tracer = factory.get_tracer("svc")
    assert tracer.__class__.__name__ == "LocalTracer"
