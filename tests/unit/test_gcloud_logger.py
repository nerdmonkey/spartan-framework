import json
from types import SimpleNamespace


def test_gcloud_happy_path_redaction_and_structured_logging(monkeypatch):
    """GCloudLogger should create structured logs and redact sensitive fields."""
    import sys
    # Patch sys.modules so imports in gcloud.py resolve to stubs
    sys.modules["google.cloud.logging"] = SimpleNamespace(Client=lambda: SimpleNamespace())
    sys.modules["google.cloud.logging_v2.handlers"] = SimpleNamespace(CloudLoggingHandler=lambda client, name=None: SimpleNamespace())

    mod = __import__("app.services.logging.gcloud", fromlist=["*"])
    monkeypatch.setattr(mod, "GCP_LOGGING_AVAILABLE", True)
    monkeypatch.setattr(mod, "env", lambda k, d=None: {"APP_ENVIRONMENT": "ci", "APP_VERSION": "9.9.9", "LOG_SAMPLE_RATE": "1.0"}.get(k, d))
    from app.services.logging.gcloud import GCloudLogger

    gw = GCloudLogger(service_name="svc", level="INFO", sample_rate=1.0)

    # Replace underlying logger with a fake that records calls
    class FakeLogger:
        def __init__(self):
            self.calls = []

        def info(self, message, extra=None):
            self.calls.append(("info", message, extra))

        def exception(self, message, extra=None):
            self.calls.append(("exception", message, extra))

    fake = FakeLogger()
    gw.logger = fake

    # Ensure sampling passes
    monkeypatch.setattr(mod.random, "random", lambda: 0.0)

    gw.info("hello", extra={"password": "pw", "safe": "yes"})

    assert fake.calls, "expected underlying logger to be called"
    _, _, extra = fake.calls[-1]
    # Structured log should have redacted password and preserved safe
    assert extra.get("password") == "[REDACTED]"
    assert extra.get("safe") == "yes"
    # Environment/version present
    assert extra.get("environment") == "ci"


def test_gcloud_sampling_blocks_logging(monkeypatch):
    """When sampling is off, no calls should be made to the underlying logger."""
    import sys
    sys.modules["google.cloud.logging"] = SimpleNamespace(Client=lambda: SimpleNamespace())
    sys.modules["google.cloud.logging_v2.handlers"] = SimpleNamespace(CloudLoggingHandler=lambda client, name=None: SimpleNamespace())

    mod = __import__("app.services.logging.gcloud", fromlist=["*"])
    monkeypatch.setattr(mod, "GCP_LOGGING_AVAILABLE", True)
    monkeypatch.setattr(mod, "env", lambda k, d=None: {"LOG_SAMPLE_RATE": "0.0", "APP_ENVIRONMENT": "ci", "APP_VERSION": "v"}.get(k, d))
    from app.services.logging.gcloud import GCloudLogger

    gw = GCloudLogger(service_name="svc", level="INFO")

    class FakeLogger:
        def __init__(self):
            self.calls = []

        def info(self, message, extra=None):
            self.calls.append(("info", message, extra))

    fake = FakeLogger()
    gw.logger = fake

    # Force random to be high so sampling fails
    monkeypatch.setattr(mod.random, "random", lambda: 1.0)

    gw.info("nope", extra={"a": 1})
    assert not fake.calls


def test_gcloud_exception_logging_and_fallback(monkeypatch):
    """exception() should call logger.exception and fallback path should set a fallback logger when handler setup fails."""
    import sys
    sys.modules["google.cloud.logging"] = SimpleNamespace(Client=lambda: SimpleNamespace())
    # Patch handler to raise
    class RaiseHandler:
        def __new__(cls, *args, **kwargs):
            raise RuntimeError("boom")
    sys.modules["google.cloud.logging_v2.handlers"] = SimpleNamespace(CloudLoggingHandler=RaiseHandler)

    mod = __import__("app.services.logging.gcloud", fromlist=["*"])
    monkeypatch.setattr(mod, "GCP_LOGGING_AVAILABLE", True)
    monkeypatch.setattr(mod, "env", lambda k, d=None: {"LOG_SAMPLE_RATE": "1.0", "APP_ENVIRONMENT": "ci", "APP_VERSION": "v"}.get(k, d))
    from app.services.logging.gcloud import GCloudLogger

    gw = GCloudLogger(service_name="svc", level="ERROR")

    # The fallback should have produced a logger object
    assert hasattr(gw, "logger")

    # Replace logger with a fake to capture exception calls
    class FakeLogger:
        def __init__(self):
            self.calls = []

        def exception(self, message, extra=None):
            self.calls.append(("exception", message, extra))

    fake = FakeLogger()
    gw.logger = fake

    # Ensure sampling allows
    monkeypatch.setattr(mod.random, "random", lambda: 0.0)

    gw.exception("err", extra={"token": "t"})

    assert fake.calls
    _, _, extra = fake.calls[-1]
    assert extra.get("token") == "[REDACTED]"
