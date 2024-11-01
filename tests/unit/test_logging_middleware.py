from unittest.mock import Mock, call

import pytest

from app.middlewares.logging import standard_logging_middleware


# Mock Lambda context object
class MockContext:
    def __init__(self):
        self.function_name = "test_function"
        self.function_version = "1.0"
        self.invoked_function_arn = (
            "arn:aws:lambda:us-west-2:123456789012:function:test_function"
        )
        self.memory_limit_in_mb = 128
        self.aws_request_id = "test_request_id"


# Sample handler function to test the middleware
def sample_handler(event, context):
    return {"statusCode": 200, "body": "Hello, world!"}


def sample_handler_with_error(event, context):
    raise ValueError("Intentional Error")


# Fixture to mock the StandardLoggerService
@pytest.fixture
def mock_logger():
    # Mock the logger without patching
    mock_logger = Mock()
    mock_logger.info = Mock()
    mock_logger.error = Mock()
    return mock_logger


# Fixture for Lambda context
@pytest.fixture
def lambda_context():
    return MockContext()


def test_standard_logging_middleware_logs_input_output(mock_logger, lambda_context):
    # Wrap the sample handler with the middleware, injecting mock_logger
    wrapped_handler = standard_logging_middleware(sample_handler, logger=mock_logger)

    # Mock event data
    event = {"key": "value"}

    # Call the handler
    response = wrapped_handler(event, lambda_context)

    # Extract logged input and output data
    input_data_size = len(str(event).encode("utf-8"))
    output_data_size = len(str(response).encode("utf-8"))

    # Check that input data was logged
    assert any(
        call[0][0] == "Input Data" and call[1]["input_data"] == event
        for call in mock_logger.info.call_args_list
    ), f"Input data log missing, call_args_list: {mock_logger.info.call_args_list}"

    # Check that output data was logged
    assert any(
        call[0][0] == "Output Data" and call[1]["output_data"] == response
        for call in mock_logger.info.call_args_list
    ), f"Output data log missing, call_args_list: {mock_logger.info.call_args_list}"

    # Verify the handler response
    assert response == {"statusCode": 200, "body": "Hello, world!"}


def test_standard_logging_middleware_logs_error(mock_logger, lambda_context):
    # Wrap the error-throwing handler with the middleware, injecting mock_logger
    wrapped_handler = standard_logging_middleware(
        sample_handler_with_error, logger=mock_logger
    )

    # Mock event data
    event = {"key": "value"}

    # Call the handler and expect an error
    with pytest.raises(ValueError, match="Intentional Error"):
        wrapped_handler(event, lambda_context)

    # Check that error details were logged once
    assert (
        mock_logger.error.called
    ), f"Expected logger.error to be called but it wasn't. Error call_args_list: {mock_logger.error.call_args_list}"
    assert any(
        "Error in Lambda function" in call[0][0]
        and "Intentional Error" in str(call[1]["error"])
        for call in mock_logger.error.call_args_list
    ), "Expected error log with 'Intentional Error' not found"


def test_standard_logging_middleware_logs_request_and_response_sizes(
    mock_logger, lambda_context
):
    # Wrap the sample handler with the middleware, injecting mock_logger
    wrapped_handler = standard_logging_middleware(sample_handler, logger=mock_logger)

    # Mock event data with a larger payload
    event = {"key": "value" * 100}

    # Call the handler
    response = wrapped_handler(event, lambda_context)

    # Calculate expected sizes
    input_data_size = len(str(event).encode("utf-8"))
    output_data_size = len(str(response).encode("utf-8"))

    # Verify that request and response sizes were logged correctly
    assert any(
        call[1].get("input_data_size") == input_data_size
        for call in mock_logger.info.call_args_list
    ), f"Input data size log missing or incorrect, call_args_list: {mock_logger.info.call_args_list}"
    assert any(
        call[1].get("output_data_size") == output_data_size
        for call in mock_logger.info.call_args_list
    ), f"Output data size log missing or incorrect, call_args_list: {mock_logger.info.call_args_list}"


def test_standard_logging_middleware_metadata_in_logs(mock_logger, lambda_context):
    # Wrap the sample handler with the middleware, injecting mock_logger
    wrapped_handler = standard_logging_middleware(sample_handler, logger=mock_logger)

    # Mock event data
    event = {"key": "value"}

    # Call the handler
    wrapped_handler(event, lambda_context)

    # Extract the logged metadata
    lambda_metadata = {
        "name": lambda_context.function_name,
        "version": lambda_context.function_version,
        "arn": lambda_context.invoked_function_arn,
        "memory_size": lambda_context.memory_limit_in_mb,
        "aws_request_id": lambda_context.aws_request_id,
    }

    # Check that the metadata was included in the logs
    assert any(
        call[1].get("lambda_function") == lambda_metadata
        for call in mock_logger.info.call_args_list
    ), f"Lambda metadata log missing or incorrect, call_args_list: {mock_logger.info.call_args_list}"
