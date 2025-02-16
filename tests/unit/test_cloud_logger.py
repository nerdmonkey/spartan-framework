from unittest.mock import patch

import pytest

from app.helpers.logger.cloud import CloudWatchLogger


@pytest.fixture
def logger():
    with patch("app.helpers.logger.cloud.Logger") as MockLogger:
        mock_logger = MockLogger.return_value
        yield CloudWatchLogger(
            service_name="test_service", level="DEBUG"
        ), mock_logger


def test_info_logging(logger):
    cloud_logger, mock_logger = logger
    cloud_logger.info("This is an info message")
    mock_logger.info.assert_called_once_with(
        "This is an info message", extra={}
    )


def test_error_logging(logger):
    cloud_logger, mock_logger = logger
    cloud_logger.error("This is an error message")
    mock_logger.error.assert_called_once_with(
        "This is an error message", extra={}
    )


def test_warning_logging(logger):
    cloud_logger, mock_logger = logger
    cloud_logger.warning("This is a warning message")
    mock_logger.warning.assert_called_once_with(
        "This is a warning message", extra={}
    )


def test_debug_logging(logger):
    cloud_logger, mock_logger = logger
    cloud_logger.debug("This is a debug message")
    mock_logger.debug.assert_called_once_with(
        "This is a debug message", extra={}
    )


def test_exception_logging(logger):
    cloud_logger, mock_logger = logger
    try:
        raise ValueError("This is an exception")
    except ValueError:
        cloud_logger.exception("Exception occurred")
    mock_logger.exception.assert_called_once_with(
        "Exception occurred", extra={}
    )


def test_critical_logging(logger):
    cloud_logger, mock_logger = logger
    cloud_logger.critical("This is a critical message")
    mock_logger.critical.assert_called_once_with(
        "This is a critical message", extra={}
    )
