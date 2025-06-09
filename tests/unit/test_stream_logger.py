from unittest.mock import MagicMock, patch

import pytest

from app.helpers.logger.stream import StreamLogger


@pytest.fixture
def mock_logger():
    mock = MagicMock()
    return mock


@pytest.fixture
def stream_logger(monkeypatch, mock_logger):
    with patch(
        "app.helpers.logger.stream.logging.getLogger", return_value=mock_logger
    ):
        logger = StreamLogger(service_name="test-service", level="DEBUG")
        return logger


def test_stream_logger_init_sets_attributes(monkeypatch, mock_logger):
    with patch(
        "app.helpers.logger.stream.logging.getLogger", return_value=mock_logger
    ):
        logger = StreamLogger(service_name="svc", level="WARNING")
        assert logger.level == "WARNING"
        assert logger.service_name == "svc"
        mock_logger.setLevel.assert_called()
        mock_logger.addHandler.assert_called()
        assert mock_logger.propagate is False


def test_format_message_includes_all_parts(stream_logger):
    msg = stream_logger._format_message("INFO", "hello", {"foo": "bar"})
    assert "[" in msg and "] [INFO]" in msg
    assert "test-service" in msg
    assert "hello" in msg
    assert "extra" in msg


def test_log_calls_logger_method(stream_logger, mock_logger):
    stream_logger.log("msg", level="INFO", extra={"a": 1})
    mock_logger.info.assert_called()
    args, kwargs = mock_logger.info.call_args
    assert "msg" in args[0]
    assert "extra" in args[0]


def test_log_fallback_to_info(stream_logger, mock_logger):
    mock_logger.reset_mock()  # Clear any calls from __init__
    # Remove the invalid level method if it exists
    if hasattr(mock_logger, "notalevel"):
        delattr(mock_logger, "notalevel")
    stream_logger.log("msg", level="NOTALEVEL", extra=None)
    assert mock_logger.info.call_count == 1


def test_info_calls_log(monkeypatch, stream_logger):
    with patch.object(stream_logger, "log") as log_patch:
        stream_logger.info("info message", extra={"a": 1})
        log_patch.assert_called_once_with(
            "info message", level="INFO", extra={"a": 1}
        )


def test_warning_calls_log(monkeypatch, stream_logger):
    with patch.object(stream_logger, "log") as log_patch:
        stream_logger.warning("warn message", extra={"b": 2})
        log_patch.assert_called_once_with(
            "warn message", level="WARNING", extra={"b": 2}
        )


def test_error_calls_log(monkeypatch, stream_logger):
    with patch.object(stream_logger, "log") as log_patch:
        stream_logger.error("error message", extra={"c": 3})
        log_patch.assert_called_once_with(
            "error message", level="ERROR", extra={"c": 3}
        )


def test_debug_calls_log(monkeypatch, stream_logger):
    with patch.object(stream_logger, "log") as log_patch:
        stream_logger.debug("debug message", extra={"d": 4})
        log_patch.assert_called_once_with(
            "debug message", level="DEBUG", extra={"d": 4}
        )


def test_exception_calls_logger_error(stream_logger, mock_logger):
    stream_logger.exception("exception message", extra={"e": 5})
    mock_logger.error.assert_called()
    args, kwargs = mock_logger.error.call_args
    assert "exception message" in args[0]
    assert "extra" in args[0]
    assert kwargs.get("exc_info") is True
