"""Unit tests for GCP logging middleware using pytest-mock conventions"""

from unittest.mock import Mock

import pytest

from app.middlewares.logging import standard_logger


class MockContext:
    """Mock generic context object for testing"""

    def __init__(self):
        pass


class MockEvent(dict):
    """Mock event object - inherits from dict for JSON serialization"""

    def __init__(self):
        super().__init__()
        self.update({"headers": {"Authorization": "Bearer token"}})

    @property
    def headers(self):
        return self.get("headers", {})


def test_standard_logger_success(mocker):
    """Test successful logging operation with proper mocking"""
    # Mock the get_logger function that standard_logger uses
    mock_logger = Mock()
    mocker.patch("app.middlewares.logging.get_logger", return_value=mock_logger)

    # Mock environment functions
    mocker.patch("app.middlewares.logging.env", return_value="test")

    # Create mock handler
    mock_handler = Mock(return_value={"statusCode": 200, "body": "success"})

    # Create wrapped handler
    wrapped_handler = standard_logger(mock_handler)

    # Execute
    result = wrapped_handler(MockEvent(), MockContext())

    # Verify result
    assert result["statusCode"] == 200
    assert result["body"] == "success"

    # Verify logger was called
    assert mock_logger.info.call_count >= 2  # Input and output logs
    mock_handler.assert_called_once()


def test_standard_logger_exception(mocker):
    """Test exception handling in logging middleware"""
    # Mock the get_logger function
    mock_logger = Mock()
    mocker.patch("app.middlewares.logging.get_logger", return_value=mock_logger)

    # Mock environment functions
    mocker.patch("app.middlewares.logging.env", return_value="test")

    # Create mock handler that raises exception
    mock_handler = Mock(side_effect=Exception("Test error"))

    # Create wrapped handler
    wrapped_handler = standard_logger(mock_handler)

    # Execute and expect exception to be re-raised
    with pytest.raises(Exception, match="Test error"):
        wrapped_handler(MockEvent(), MockContext())

    # Verify error was logged
    mock_logger.error.assert_called_once()
    error_call = mock_logger.error.call_args
    assert "Function error" in error_call[0][0]
    assert "event_type" in error_call[1]["extra"]
    assert error_call[1]["extra"]["event_type"] == "function_error"


def test_standard_logger_input_output_logging(mocker):
    """Test that input and output data are logged"""
    # Mock the get_logger function
    mock_logger = Mock()
    mocker.patch("app.middlewares.logging.get_logger", return_value=mock_logger)

    # Mock environment functions
    mocker.patch("app.middlewares.logging.env", return_value="test")

    # Create test data - use dict instead of MockEvent for cleaner testing
    test_event = {"test": "input_data"}
    test_response = {"statusCode": 200, "body": "test_output"}

    mock_handler = Mock(return_value=test_response)
    wrapped_handler = standard_logger(mock_handler)

    # Execute
    result = wrapped_handler(test_event, MockContext())

    # Verify result
    assert result == test_response

    # Verify input and output logging
    assert mock_logger.info.call_count == 2

    # Check input log
    input_call = mock_logger.info.call_args_list[0]
    assert "Function invoked" in input_call[0][0]
    assert "input_data" in input_call[1]["extra"]
    assert input_call[1]["extra"]["input_data"] == test_event
    assert input_call[1]["extra"]["event_type"] == "function_input"

    # Check output log
    output_call = mock_logger.info.call_args_list[1]
    assert "Function completed" in output_call[0][0]
    assert "output_data" in output_call[1]["extra"]
    assert output_call[1]["extra"]["output_data"] == test_response
    assert output_call[1]["extra"]["event_type"] == "function_output"


def test_standard_logger_debug_mode(mocker):
    """Test debug mode behavior with local environment"""
    # Mock the get_logger function
    mock_logger = Mock()
    mocker.patch("app.middlewares.logging.get_logger", return_value=mock_logger)

    # Mock environment to return local and debug
    def mock_env_side_effect(key, default=None):
        return {
            "APP_ENVIRONMENT": "local",
            "APP_DEBUG": "true",
            "APP_NAME": "test-service",
        }.get(key, default or "")

    mocker.patch("app.middlewares.logging.env", side_effect=mock_env_side_effect)

    # Mock print function
    mock_print = mocker.patch("builtins.print")

    mock_handler = Mock(return_value={"statusCode": 200})
    wrapped_handler = standard_logger(mock_handler)

    # Execute
    wrapped_handler(MockEvent(), MockContext())

    # Verify print was called for debug output
    assert mock_print.call_count == 2  # Input and output debug prints

    # Verify normal logging still works
    assert mock_logger.info.call_count == 2


def test_standard_logger_custom_logger(mocker):
    """Test using a custom logger parameter"""
    # Create custom mock logger
    custom_logger = Mock()

    # Mock environment functions
    mocker.patch("app.middlewares.logging.env", return_value="test")

    mock_handler = Mock(return_value={"statusCode": 200})

    # Use custom logger
    wrapped_handler = standard_logger(mock_handler, logger=custom_logger)

    # Execute
    wrapped_handler(MockEvent(), MockContext())

    # Verify custom logger was used
    assert custom_logger.info.call_count == 2
    assert custom_logger.error.call_count == 0


def test_standard_logger_data_size_calculation(mocker):
    """Test that data size is calculated and logged"""
    # Mock the get_logger function
    mock_logger = Mock()
    mocker.patch("app.middlewares.logging.get_logger", return_value=mock_logger)

    # Mock environment functions
    mocker.patch("app.middlewares.logging.env", return_value="test")

    # Create test data with known size - use dict for predictable serialization
    test_event = {"data": "x" * 100}  # Predictable size
    test_response = {"result": "y" * 50}

    mock_handler = Mock(return_value=test_response)
    wrapped_handler = standard_logger(mock_handler)

    # Execute
    wrapped_handler(test_event, MockContext())

    # Verify size calculations are logged
    input_call = mock_logger.info.call_args_list[0]
    output_call = mock_logger.info.call_args_list[1]

    assert "input_data_size" in input_call[1]["extra"]
    assert "output_data_size" in output_call[1]["extra"]

    # Size should be greater than 0
    assert input_call[1]["extra"]["input_data_size"] > 0
    assert output_call[1]["extra"]["output_data_size"] > 0


def test_standard_logger_gcp_cloud_functions_context(mocker):
    """Test GCP Cloud Functions context detection"""
    # Mock the get_logger function
    mock_logger = Mock()
    mocker.patch("app.middlewares.logging.get_logger", return_value=mock_logger)

    # Mock environment for GCP Cloud Functions
    def mock_env_side_effect(key, default=None):
        return {
            "FUNCTION_NAME": "my-gcp-function",
            "FUNCTION_REGION": "us-central1",
            "APP_NAME": "test-service",
        }.get(key, default or "")

    mocker.patch("app.middlewares.logging.env", side_effect=mock_env_side_effect)

    # Create GCP Cloud Functions context
    class GCPContext:
        event_id = "test-event-123"
        event_type = "google.pubsub.topic.publish"
        request_id = "gcp-request-456"

    mock_handler = Mock(return_value={"success": True})
    wrapped_handler = standard_logger(mock_handler)

    # Execute
    wrapped_handler({"message": "test"}, GCPContext())

    # Verify GCP context is logged
    input_call = mock_logger.info.call_args_list[0]
    function_info = input_call[1]["extra"]["function"]

    assert function_info["platform"] == "gcp_cloud_functions"
    assert function_info["name"] == "my-gcp-function"
    assert function_info["region"] == "us-central1"
    assert function_info["event_id"] == "test-event-123"
    assert function_info["event_type"] == "google.pubsub.topic.publish"


def test_standard_logger_gcp_cloud_run_context(mocker):
    """Test GCP Cloud Run context detection"""
    # Mock the get_logger function
    mock_logger = Mock()
    mocker.patch("app.middlewares.logging.get_logger", return_value=mock_logger)

    # Mock environment for GCP Cloud Run
    def mock_env_side_effect(key, default=None):
        return {
            "K_SERVICE": "my-cloud-run-service",
            "K_REVISION": "my-cloud-run-service-00001-abc",
            "K_CONFIGURATION": "my-cloud-run-service",
            "FUNCTION_REGION": "us-east1",
            "APP_NAME": "test-service",
        }.get(key, default or "")

    mocker.patch("app.middlewares.logging.env", side_effect=mock_env_side_effect)

    # Create generic context (Cloud Run doesn't have specific context)
    class GenericContext:
        pass

    mock_handler = Mock(return_value={"status": "ok"})
    wrapped_handler = standard_logger(mock_handler)

    # Execute
    wrapped_handler({"request": "data"}, GenericContext())

    # Verify Cloud Run context is logged
    input_call = mock_logger.info.call_args_list[0]
    function_info = input_call[1]["extra"]["function"]

    assert function_info["platform"] == "gcp_cloud_run"
    assert function_info["service"] == "my-cloud-run-service"
    assert function_info["revision"] == "my-cloud-run-service-00001-abc"
    assert function_info["region"] == "us-east1"
