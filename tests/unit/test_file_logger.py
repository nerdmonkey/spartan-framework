import json
import logging
import os
from unittest.mock import patch

import pytest

from app.helpers.logger.file import FileLogger


@pytest.fixture(scope="module")
def log_dir():
    dir_path = "test_logs"
    os.makedirs(dir_path, exist_ok=True)
    yield dir_path
    if os.path.exists(dir_path):
        for file in os.listdir(dir_path):
            os.remove(os.path.join(dir_path, file))
        os.rmdir(dir_path)


@pytest.fixture
def logger(log_dir):
    logging.basicConfig(level=logging.DEBUG)
    logger = FileLogger(
        service_name="test_service", log_dir=log_dir, level="DEBUG"
    )

    if not logger.logger.handlers:
        logger.logger.addHandler(logging.StreamHandler())
    return logger


@pytest.fixture
def log_file(log_dir):
    return f"{log_dir}/spartan.log"


@pytest.fixture(autouse=True)
def clear_log_file(log_file):
    if os.path.exists(log_file):
        os.remove(log_file)


@pytest.fixture
def mock_logger():
    with patch("app.helpers.logger.get_logger") as mock_get_logger:
        mock_logger = logging.getLogger("mock_logger")
        mock_get_logger.return_value = mock_logger
        yield mock_logger


def test_info_logging(mock_logger):
    mock_logger.info("This is an info message")


def test_error_logging(mock_logger):
    mock_logger.error("Test error message")


def test_warning_logging(mock_logger):
    mock_logger.warning("Test warning message")


def test_debug_logging(mock_logger):
    mock_logger.debug("Test debug message")


def test_exception_logging(mock_logger):
    mock_logger.exception("Test exception message")


def test_critical_logging(mock_logger):
    mock_logger.critical("Test critical message")


def _assert_log_contains(log_file, level, message):
    with open(log_file, "r") as f:
        log_content = f.read().strip()
        print(f"Log content: {log_content}")  # Debugging print statement
        if log_content:
            log_entry = json.loads(log_content.split("\n")[-1])
            print(f"Log entry: {log_entry}")  # Debugging print statement
            assert log_entry["level"] == level
            assert log_entry["message"] == message
        else:
            pytest.fail("Log file is empty")
