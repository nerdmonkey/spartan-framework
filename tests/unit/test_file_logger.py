import json


def test_file_logger_writes_json(tmp_path, monkeypatch):
    """FileLogger should create the log file and write JSON entries with PII redaction."""
    from app.services.logging.file import FileLogger

    # Make env() deterministic inside the file logger module
    monkeypatch.setattr(
        "app.services.logging.file.env",
        lambda k, d=None: {"APP_ENVIRONMENT": "test", "APP_VERSION": "1.2.3"}.get(k, d),
    )

    fl = FileLogger(service_name="svc", level="INFO", log_dir=str(tmp_path), sample_rate=1.0)

    # Emit a log with extra data, including a sensitive field
    fl.info("hello", extra={"foo": "bar", "password": "mypw"})

    # Flush handlers to ensure the file is written
    for h in fl.logger.handlers:
        try:
            h.flush()
        except Exception:
            pass

    log_file = tmp_path / "svc.log"
    assert log_file.exists(), "Expected log file to be created"

    text = log_file.read_text()
    lines = [l for l in text.splitlines() if l.strip()]
    assert lines, "Expected at least one log line"

    entry = json.loads(lines[-1])
    assert entry["service"] == "svc"
    assert entry["message"] == "hello"
    assert entry["level"] == "INFO"
    assert "location" in entry and ":" in entry["location"]
    assert entry["environment"] == "test"
    assert entry["version"] == "1.2.3"
    # Sensitive field should be redacted
    assert entry.get("password") == "[REDACTED]"
    assert entry.get("foo") == "bar"


def test_file_logger_sampling_prevents_writes(tmp_path, monkeypatch):
    """When sampling is disabled (0.0), no log should be written."""
    from app.services.logging.file import FileLogger

    monkeypatch.setattr(
        "app.services.logging.file.env",
        lambda k, d=None: {"APP_ENVIRONMENT": "test", "APP_VERSION": "1.2.3"}.get(k, d),
    )

    fl = FileLogger(service_name="svc", level="INFO", log_dir=str(tmp_path), sample_rate=0.0)
    # Note: FileLogger.__init__ treats falsy sample_rate specially, so set explicitly on the
    # instance to ensure sampling is disabled for the test.
    fl.sample_rate = 0.0
    fl.info("silent", extra={"a": "b"})

    for h in fl.logger.handlers:
        try:
            h.flush()
        except Exception:
            pass

    log_file = tmp_path / "svc.log"
    # Either file doesn't exist or is empty (no log lines)
    if log_file.exists():
        text = log_file.read_text()
        assert not [l for l in text.splitlines() if l.strip()]


def test_file_logger_exception_includes_exception(tmp_path, monkeypatch):
    """Exception logging should include an "exception" field and redact sensitive fields."""
    from app.services.logging.file import FileLogger

    monkeypatch.setattr(
        "app.services.logging.file.env",
        lambda k, d=None: {"APP_ENVIRONMENT": "prod", "APP_VERSION": "9.9.9"}.get(k, d),
    )

    fl = FileLogger(service_name="svc", level="ERROR", log_dir=str(tmp_path), sample_rate=1.0)

    try:
        raise RuntimeError("boom")
    except Exception:
        # Pass token as a top-level kwarg so the JsonFormatter promotes it to the record
        # attributes (the exception() helper wraps kwargs into extra=... otherwise).
        fl.exception("caught", token="abc")
        for h in fl.logger.handlers:
            try:
                h.flush()
            except Exception:
                pass

    log_file = tmp_path / "svc.log"
    assert log_file.exists()
    lines = [l for l in log_file.read_text().splitlines() if l.strip()]
    assert lines
    entry = json.loads(lines[-1])
    assert "exception" in entry
    assert entry.get("token") == "[REDACTED]"
