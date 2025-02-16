import logging
from unittest.mock import patch

import pytest

from app.helpers.logger.base import BaseLogger


class MockLogger(BaseLogger):
    def __init__(self):
        self.logger = logging.getLogger("test_service")

    def info(self, message: str):
        self.logger.info(message)

    def warning(self, message: str):
        self.logger.warning(message)

    def error(self, message: str):
        self.logger.error(message)

    def debug(self, message: str):
        self.logger.debug(message)

    def critical(self, message: str):
        self.logger.critical(message)

    def exception(self, message: str):
        self.logger.exception(message)


@pytest.fixture
def logger():
    logger = MockLogger()
    logger.service_name = "test_service"
    return logger


def test_logger_initialization(logger):
    assert logger.service_name == "test_service"
    assert isinstance(logger.logger, logging.Logger)


def test_log_info(logger):
    with patch.object(logger.logger, "info") as mock_info:
        logger.info("test message")
        mock_info.assert_called_once_with("test message")


def test_log_warning(logger):
    with patch.object(logger.logger, "warning") as mock_warning:
        logger.warning("test message")
        mock_warning.assert_called_once_with("test message")


def test_log_error(logger):
    with patch.object(logger.logger, "error") as mock_error:
        logger.error("test message")
        mock_error.assert_called_once_with("test message")


def test_log_debug(logger):
    with patch.object(logger.logger, "debug") as mock_debug:
        logger.debug("test message")
        mock_debug.assert_called_once_with("test message")


def test_log_critical(logger):
    with patch.object(logger.logger, "critical") as mock_critical:
        logger.critical("test message")
        mock_critical.assert_called_once_with("test message")


def test_log_exception(logger):
    with patch.object(logger.logger, "exception") as mock_exception:
        logger.exception("test message")
        mock_exception.assert_called_once_with("test message")
