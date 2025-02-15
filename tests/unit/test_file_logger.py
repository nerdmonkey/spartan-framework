import json
import logging
import os

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


def test_info_logging(logger, log_file):
    logger.info("This is an info message")
    _assert_log_contains(log_file, "INFO", "This is an info message")


def test_error_logging(logger, log_file):
    logger.error("This is an error message")
    _assert_log_contains(log_file, "ERROR", "This is an error message")


def test_warning_logging(logger, log_file):
    logger.warning("This is a warning message")
    _assert_log_contains(log_file, "WARNING", "This is a warning message")


def test_debug_logging(logger, log_file):
    logger.debug("This is a debug message")
    _assert_log_contains(log_file, "DEBUG", "This is a debug message")


def test_exception_logging(logger, log_file):
    try:
        raise ValueError("This is an exception")
    except ValueError:
        logger.exception("Exception occurred")
    _assert_log_contains(log_file, "ERROR", "Exception occurred")


def test_critical_logging(logger, log_file):
    logger.critical("This is a critical message")
    _assert_log_contains(log_file, "CRITICAL", "This is a critical message")


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
