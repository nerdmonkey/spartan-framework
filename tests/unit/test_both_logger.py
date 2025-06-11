from unittest.mock import MagicMock, patch

import pytest

from app.helpers.logger.both import BothLogger, _prettify_extra


@pytest.fixture
def mock_file_logger():
    mock = MagicMock()
    return mock


@pytest.fixture
def mock_stream_logger():
    mock = MagicMock()
    return mock


@pytest.fixture
def both_logger(monkeypatch, mock_file_logger, mock_stream_logger):
    with patch(
        "app.helpers.logger.both.FileLogger", return_value=mock_file_logger
    ), patch(
        "app.helpers.logger.both.StreamLogger", return_value=mock_stream_logger
    ):
        logger = BothLogger(service_name="test-service", level="DEBUG")
        return logger


def test_prettify_extra_none():
    assert _prettify_extra(None) == ""
    assert _prettify_extra("") == ""


def test_prettify_extra_json():
    extra = {"foo": "bar"}
    result = _prettify_extra(extra)
    assert result.startswith(" | extra: ")
    assert '"foo": "bar"' in result


def test_prettify_extra_nonserializable():
    class NonSerializable:
        pass

    extra = NonSerializable()
    result = _prettify_extra(extra)
    assert result.startswith(" | extra: ")
    assert "NonSerializable" in result


def test_log_calls_both_loggers(
    both_logger, mock_file_logger, mock_stream_logger
):
    both_logger.log("msg", level="INFO")
    mock_file_logger.log.assert_called_once_with("msg", "INFO")
    mock_stream_logger.log.assert_called_once_with("msg", "INFO")


def test_info_calls_both_loggers(
    both_logger, mock_file_logger, mock_stream_logger
):
    both_logger.info("info message", extra={"a": 1})
    mock_file_logger.info.assert_called_once_with(
        "info message", extra={"a": 1}, stacklevel=6
    )
    # The stream_logger gets prettified extra
    args, kwargs = mock_stream_logger.info.call_args
    assert "info message" in args[0]
    assert "extra" in args[0]


def test_warning_calls_both_loggers(
    both_logger, mock_file_logger, mock_stream_logger
):
    both_logger.warning("warn message", extra={"b": 2})
    mock_file_logger.warning.assert_called_once_with(
        "warn message", extra={"b": 2}, stacklevel=6
    )
    args, kwargs = mock_stream_logger.warning.call_args
    assert "warn message" in args[0]
    assert "extra" in args[0]


def test_error_calls_both_loggers(
    both_logger, mock_file_logger, mock_stream_logger
):
    both_logger.error("error message", extra={"c": 3})
    mock_file_logger.error.assert_called_once_with(
        "error message", extra={"c": 3}, stacklevel=6
    )
    args, kwargs = mock_stream_logger.error.call_args
    assert "error message" in args[0]
    assert "extra" in args[0]


def test_debug_calls_both_loggers(
    both_logger, mock_file_logger, mock_stream_logger
):
    both_logger.debug("debug message", extra={"d": 4})
    mock_file_logger.debug.assert_called_once_with(
        "debug message", extra={"d": 4}, stacklevel=6
    )
    args, kwargs = mock_stream_logger.debug.call_args
    assert "debug message" in args[0]
    assert "extra" in args[0]


def test_exception_calls_both_loggers(
    both_logger, mock_file_logger, mock_stream_logger
):
    both_logger.exception("exception message", extra={"e": 5})
    mock_file_logger.exception.assert_called_once_with(
        "exception message", extra={"e": 5}, stacklevel=6
    )
    mock_stream_logger.exception.assert_called_once_with(
        "exception message", extra={"e": 5}
    )


def test_logger_init_sets_attributes(monkeypatch):
    with patch("app.helpers.logger.both.FileLogger") as file_patch, patch(
        "app.helpers.logger.both.StreamLogger"
    ) as stream_patch:
        logger = BothLogger(service_name="svc", level="WARNING")
        assert logger.level == "WARNING"
        assert logger.service_name == "svc"
        file_patch.assert_called_once_with(service_name="svc", level="WARNING")
        stream_patch.assert_called_once_with(
            service_name="svc", level="WARNING"
        )
