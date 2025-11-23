import json
from types import SimpleNamespace


def test_cloudwatch_logger_format_and_redaction(monkeypatch):
    """CloudWatchLogger should use custom formatter to add env/version and redact sensitive fields."""
    # Replace the Logger used in the module with a fake implementation
    class FakeHandler:
        def __init__(self):
            class Formatter:
                def format(self, record):
                    # Original formatter returns JSON with message and extra
                    return json.dumps({
                        "message": record.getMessage(),
                        "extra": getattr(record, "extra", {}),
                    })

            self.formatter = Formatter()

    class FakeInnerLogger:
        def __init__(self):
            self.handlers = [FakeHandler()]

    class FakeLogger:
        def __init__(self, *args, **kwargs):
            # mimic aws_lambda_powertools.Logger internal logger
            self._logger = FakeInnerLogger()
            self.calls = []

        def _emit(self, record):
            # Not used, kept for parity
            pass

        def _collect(self, formatted):
            # store formatted message for assertions
            self.last = formatted

        def info(self, message, extra=None, caller_location=None):
            record = SimpleNamespace()
            record.getMessage = lambda: message
            record.extra = extra or {}
            if caller_location is not None:
                record.caller_location = caller_location
            record.pathname = __file__
            record.lineno = 10
            # Call the (possibly monkey-patched) formatter(s)
            out = None
            for h in self._logger.handlers:
                out = h.formatter.format(record)
            self.last = out
            self.calls.append(("info", message, extra, caller_location))

        def error(self, message, extra=None, caller_location=None):
            return self.info(message, extra=extra, caller_location=caller_location)

        def warning(self, message, extra=None, caller_location=None):
            return self.info(message, extra=extra, caller_location=caller_location)

        def debug(self, message, extra=None, caller_location=None):
            return self.info(message, extra=extra, caller_location=caller_location)

        def exception(self, message, extra=None, caller_location=None):
            return self.info(message, extra=extra, caller_location=caller_location)

        def critical(self, message, extra=None, caller_location=None):
            return self.info(message, extra=extra, caller_location=caller_location)

        def inject_lambda_context(self, *args, **kwargs):
            # Return a no-op decorator for testing
            def decorator(f=None):
                if f is None:
                    return lambda fn: fn
                return f

            return decorator

    # Monkeypatch module-level dependencies before creating CloudWatchLogger
    import app.services.logging.cloud as cloud_mod

    monkeypatch.setattr(cloud_mod, "Logger", FakeLogger)
    monkeypatch.setattr(cloud_mod, "env", lambda k, d=None: {"APP_ENVIRONMENT": "ci", "APP_VERSION": "9.9.9", "LOG_SAMPLE_RATE": "1.0"}.get(k, d))

    # Create logger and call info with sensitive data in extra
    from app.services.logging.cloud import CloudWatchLogger

    cw = CloudWatchLogger(service_name="svc", level="INFO", sample_rate=1.0)

    # Call info with token in extra which should be redacted by custom formatter
    cw.info("hello", token="secrettoken", extra={"api_key": "k", "safe": "v"})

    # The FakeLogger stored the last formatted JSON string
    formatted = json.loads(cw.logger.last)
    # Environment/version should be injected by custom formatter
    assert formatted["environment"] == "ci"
    assert formatted["version"] == "9.9.9"
    # At least one sensitive field should be redacted somewhere in the output
    assert "[REDACTED]" in cw.logger.last
    # Non-sensitive field should be present somewhere in the output
    def contains_value(obj, val):
        if isinstance(obj, dict):
            return any(contains_value(v, val) for v in obj.values())
        if isinstance(obj, list):
            return any(contains_value(v, val) for v in obj)
        return obj == val

    assert contains_value(formatted, "v")


def test_cloudwatch_logger_sampling_and_inject(monkeypatch):
    """Sampling should prevent logs when sample_rate is low and inject_lambda_context returns decorator."""
    class DummyLogger:
        def __init__(self, *args, **kwargs):
            class H:
                class F:
                    def format(self, r):
                        return json.dumps({"message": r.getMessage(), "extra": getattr(r, "extra", {})})

                formatter = F()

            self._logger = SimpleNamespace(handlers=[H()])
            self.calls = []

        def info(self, message, extra=None, caller_location=None):
            self.calls.append(("info", message, extra, caller_location))

        def inject_lambda_context(self, *args, **kwargs):
            return lambda f: f

    import app.services.logging.cloud as cloud_mod
    monkeypatch.setattr(cloud_mod, "Logger", DummyLogger)
    monkeypatch.setattr(cloud_mod, "env", lambda k, d=None: {"LOG_SAMPLE_RATE": "0.0", "APP_ENVIRONMENT": "x", "APP_VERSION": "y"}.get(k, d))

    from app.services.logging.cloud import CloudWatchLogger

    cw = CloudWatchLogger(service_name="svc", level="INFO")

    # Force sampling to drop logs by setting sample_rate 0.0 and making random.random return 1.0
    cw.sample_rate = 0.0
    monkeypatch.setattr(cloud_mod.random, "random", lambda: 1.0)

    cw.info("should_not_log", extra={"a": "b"})
    # DummyLogger should have no calls recorded
    assert not getattr(cw.logger, "calls", None)

    # inject_lambda_context should return a callable (decorator)
    deco = cw.inject_lambda_context()
    assert callable(deco)
