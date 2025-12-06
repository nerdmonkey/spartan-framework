from unittest.mock import MagicMock

from app.services.logging.both import BothLogger, _prettify_extra


def test_prettify_extra_empty():
    """Test prettify extra with empty input."""
    assert _prettify_extra(None) == ""
    assert _prettify_extra({}) == ""


def test_prettify_extra_with_data():
    """Test prettify extra with normal data."""
    result = _prettify_extra({"name": "value", "num": 123})
    assert "extra:" in result
    assert "name" in result
    assert "value" in result


def test_prettify_extra_redacts_sensitive_data():
    """Test prettify extra redacts sensitive fields."""
    result = _prettify_extra({"password": "secret123", "username": "alice"})
    assert "[REDACTED]" in result
    assert "secret123" not in result
    assert "alice" in result


def test_prettify_extra_handles_serialization_error():
    """Test prettify extra handles non-serializable data."""

    class NonSerializable:
        pass

    result = _prettify_extra({"obj": NonSerializable()})
    assert "extra:" in result


def test_both_logger_initialization():
    """Test BothLogger initializes with file and stream loggers."""
    logger = BothLogger("test-service", level="DEBUG")
    assert logger.service_name == "test-service"
    assert logger.level == "DEBUG"
    assert logger.file_logger is not None
    assert logger.stream_logger is not None


def test_both_logger_log():
    """Test BothLogger.log delegates to both loggers."""
    logger = BothLogger("test-service")
    logger.file_logger = MagicMock()
    logger.stream_logger = MagicMock()

    logger.log("test message", "INFO")

    logger.file_logger.log.assert_called_once_with("test message", "INFO")
    logger.stream_logger.log.assert_called_once_with("test message", "INFO")


def test_both_logger_info_with_extra():
    """Test BothLogger.info with extra data."""
    logger = BothLogger("test-service")
    logger.file_logger = MagicMock()
    logger.stream_logger = MagicMock()

    logger.info("test message", extra={"key": "value"})

    logger.file_logger.info.assert_called_once()
    logger.stream_logger.info.assert_called_once()
    stream_call_args = logger.stream_logger.info.call_args[0][0]
    assert "extra:" in stream_call_args


def test_both_logger_warning_with_extra():
    """Test BothLogger.warning with extra data."""
    logger = BothLogger("test-service")
    logger.file_logger = MagicMock()
    logger.stream_logger = MagicMock()

    logger.warning("warning message", extra={"status": "warn"})

    logger.file_logger.warning.assert_called_once()
    logger.stream_logger.warning.assert_called_once()


def test_both_logger_error_with_extra():
    """Test BothLogger.error with extra data."""
    logger = BothLogger("test-service")
    logger.file_logger = MagicMock()
    logger.stream_logger = MagicMock()

    logger.error("error message", extra={"code": 500})

    logger.file_logger.error.assert_called_once()
    logger.stream_logger.error.assert_called_once()


def test_both_logger_debug_with_extra():
    """Test BothLogger.debug with extra data."""
    logger = BothLogger("test-service")
    logger.file_logger = MagicMock()
    logger.stream_logger = MagicMock()

    logger.debug("debug message", extra={"trace": "xyz"})

    logger.file_logger.debug.assert_called_once()
    logger.stream_logger.debug.assert_called_once()


def test_both_logger_exception_with_extra():
    """Test BothLogger.exception with extra data."""
    logger = BothLogger("test-service")
    logger.file_logger = MagicMock()
    logger.stream_logger = MagicMock()

    logger.exception("exception occurred", extra={"error": "details"})

    logger.file_logger.exception.assert_called_once()
    logger.stream_logger.exception.assert_called_once()
