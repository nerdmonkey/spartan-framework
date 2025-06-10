from unittest.mock import patch

import pytest

from app.services.logging import StandardLoggerService


@pytest.fixture
def mock_logger():
    with patch(
        "app.services.logging.LoggerFactory.create_logger"
    ) as MockLogger:
        mock_instance = MockLogger.return_value
        yield mock_instance


@pytest.fixture
def logging(mock_logger):
    return StandardLoggerService()


def test_logger_info_called(logging, mock_logger):
    message = "Test info message"
    logging.info(message, key="value")

    mock_logger.info.assert_called_once_with(message, key="value")


def test_logger_error_called(logging, mock_logger):
    message = "Test error message"
    logging.error(message, error="TestError")

    mock_logger.error.assert_called_once_with(message, error="TestError")


def test_logger_debug_called(logging, mock_logger):
    message = "Test debug message"
    logging.debug(message, debug_data="sample")

    mock_logger.debug.assert_called_once_with(message, debug_data="sample")


def test_logger_critical_called(logging, mock_logger):
    message = "Test critical message"
    logging.critical(message, critical_data="urgent")

    mock_logger.critical.assert_called_once_with(
        message, critical_data="urgent"
    )


def test_logger_exception_called(logging, mock_logger):
    message = "Test exception message"
    logging.exception(message, exception="ExampleException")

    mock_logger.exception.assert_called_once_with(
        message, exception="ExampleException"
    )


def test_logger_warning_called(logging, mock_logger):
    message = "Test warning message"
    logging.warning(message, warning="TestWarning")

    mock_logger.warning.assert_called_once_with(message, warning="TestWarning")


def test_set_level_changes_logger_level(logging, mock_logger):
    mock_logger.setLevel.side_effect = lambda level: setattr(mock_logger, "level", level)

    logging.set_level("DEBUG")

    mock_logger.setLevel.assert_called_once_with("DEBUG")
    assert getattr(mock_logger, "level", None) == "DEBUG"


def test_get_logger_returns_underlying_logger(logging, mock_logger):
    assert logging.get_logger() is mock_logger
