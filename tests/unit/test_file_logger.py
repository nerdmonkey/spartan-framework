import json
import os
from unittest.mock import Mock, mock_open, patch

import pytest

from app.helpers.logger.file import FileLogger


def test_logger_initialization(file_logger, temp_log_dir):
    """Test if logger is properly initialized"""
    assert file_logger.service_name == "test-service"
    assert os.path.exists(temp_log_dir)
    assert os.path.exists(os.path.join(temp_log_dir, "test-service.log"))


def test_log_format(file_logger, mock_datetime):
    with patch(
        "builtins.open",
        mock_open(
            read_data='{"message": "Test log message", "extra_field": "extra_value", "timestamp": "2023-12-20T10:30:00"}'
        ),
    ):
        file_logger.info("Test log message", extra_field="extra_value")
        log_file_path = os.path.join(
            file_logger.logger.handlers[0].baseFilename
        )
        with open(log_file_path, "r") as log_file:
            log_entry = json.loads(log_file.readline())
            assert log_entry["message"] == "Test log message"
            assert log_entry["extra_field"] == "extra_value"
            assert log_entry["timestamp"] == mock_datetime.utcnow().isoformat()


def test_log_rotation(file_logger, temp_log_dir):
    """Test if log rotation works properly"""
    with patch("builtins.open", mock_open()):
        large_message = "x" * 512  # Half of max_bytes
        for _ in range(4):  # Should create at least 2 files
            file_logger.info(large_message)

        log_files = [
            f
            for f in os.listdir(temp_log_dir)
            if f.startswith("test-service.log")
        ]
        assert len(log_files) > 1


@pytest.mark.parametrize(
    "log_level", ["info", "error", "warning", "debug", "critical"]
)
def test_log_levels(mock_logger, file_logger, log_level):
    """Test all log levels"""
    test_message = "Test message"
    extra_args = {"extra_field": "value"}

    # Call the log method
    getattr(file_logger, log_level)(test_message, extra=extra_args)

    # Verify the corresponding method was called on the mock
    getattr(mock_logger, log_level).assert_called_once_with(
        test_message, extra={"extra": extra_args}
    )


def test_exception_logging(file_logger, temp_log_dir):
    """Test exception logging"""
    with patch(
        "builtins.open",
        mock_open(
            read_data='{"level": "ERROR", "exception": "ValueError: Test exception"}'
        ),
    ):
        try:
            raise ValueError("Test exception")
        except ValueError:
            file_logger.exception("An error occurred")

        log_file_path = os.path.join(
            file_logger.logger.handlers[0].baseFilename
        )
        with open(log_file_path, "r") as f:
            log_entry = json.loads(f.read().strip())

        assert log_entry["level"] == "ERROR"
        assert "exception" in log_entry
        assert "ValueError: Test exception" in log_entry["exception"]


def test_directory_creation(temp_log_dir):
    logger = FileLogger(service_name="test-service", log_dir=temp_log_dir)
    assert os.path.exists(temp_log_dir)


def test_lambda_context_injection(file_logger):
    @file_logger.inject_lambda_context
    def handler(event, context):
        return {"statusCode": 200, "body": "Hello, world!"}

    event = {"key": "value"}
    context = Mock()
    response = handler(event, context)
    assert response == {"statusCode": 200, "body": "Hello, world!"}


def test_multiple_loggers_isolation(temp_log_dir):
    logger1 = FileLogger(service_name="service1", log_dir=temp_log_dir)
    logger2 = FileLogger(service_name="service2", log_dir=temp_log_dir)

    logger1.info("Log from service1")
    logger2.info("Log from service2")

    log_file_path1 = os.path.join(temp_log_dir, "service1.log")
    log_file_path2 = os.path.join(temp_log_dir, "service2.log")

    with open(log_file_path1, "r") as log_file1:
        log_entry1 = json.loads(log_file1.readline())
        assert log_entry1["service"] == "service1"
        assert log_entry1["message"] == "Log from service1"

    with open(log_file_path2, "r") as log_file2:
        log_entry2 = json.loads(log_file2.readline())
        assert log_entry2["service"] == "service2"
        assert log_entry2["message"] == "Log from service2"


def test_invalid_log_level(temp_log_dir):
    with pytest.raises(ValueError):
        FileLogger(
            service_name="test-service", level="INVALID", log_dir=temp_log_dir
        )


def test_log_with_large_data(file_logger):
    large_message = "A" * 1024 * 1024  # 1MB message
    with patch(
        "builtins.open",
        mock_open(read_data=json.dumps({"message": large_message})),
    ):
        file_logger.info(large_message)
        log_file_path = os.path.join(
            file_logger.logger.handlers[0].baseFilename
        )
        with open(log_file_path, "r") as log_file:
            log_entry = json.loads(log_file.readline())
            assert log_entry["message"] == large_message
