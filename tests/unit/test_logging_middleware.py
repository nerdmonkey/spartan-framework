from unittest.mock import Mock

import pytest

from app.middlewares.logging import standard_logger


class MockContext:
    def __init__(self):
        self.function_name = "test_function"
        self.function_version = "1.0"
        self.invoked_function_arn = (
            "arn:aws:lambda:us-west-2:123456789012:function:test_function"
        )
        self.memory_limit_in_mb = 128
        self.aws_request_id = "test_request_id"


def sample_handler(event, context):
    return {"statusCode": 200, "body": "Hello, world!"}


def sample_handler_with_error(event, context):
    raise ValueError("Intentional Error")


@pytest.fixture
def mock_logger():
    mock_logger = Mock()
    mock_logger.info = Mock()
    mock_logger.error = Mock()
    return mock_logger


@pytest.fixture
def lambda_context():
    return MockContext()


def test_standard_logger_logs_input_output(mock_logger, lambda_context):
    event = {"key": "value"}

    @standard_logger(logger=mock_logger)
    def wrapped_handler(event, context):
        return sample_handler(event, context)

    response = wrapped_handler(event, lambda_context)

    # Check input logging
    input_call = mock_logger.info.call_args_list[0]
    assert "Lambda function invoked" in input_call[0]
    assert input_call[1]["extra"]["input_data"] == event

    # Check output logging
    output_call = mock_logger.info.call_args_list[1]
    assert "Lambda function completed successfully" in output_call[0]
    assert output_call[1]["extra"]["output_data"] == response


def test_standard_logger_logs_error(mock_logger, lambda_context):
    event = {"key": "value"}

    @standard_logger(logger=mock_logger)
    def wrapped_handler(event, context):
        return sample_handler_with_error(event, context)

    with pytest.raises(ValueError, match="Intentional Error"):
        wrapped_handler(event, lambda_context)

    error_call = mock_logger.error.call_args
    assert "Error in Lambda function" in error_call[0]
    assert "Intentional Error" in error_call[1]["extra"]["error"]


def test_standard_logger_logs_request_and_response_sizes(
    mock_logger, lambda_context
):
    event = {"key": "value" * 100}

    @standard_logger(logger=mock_logger)
    def wrapped_handler(event, context):
        return sample_handler(event, context)

    response = wrapped_handler(event, lambda_context)

    input_data_size = len(str(event).encode("utf-8"))
    output_data_size = len(str(response).encode("utf-8"))

    # Check input size logging
    input_call = mock_logger.info.call_args_list[0]
    assert input_call[1]["extra"]["input_data_size"] == input_data_size

    # Check output size logging
    output_call = mock_logger.info.call_args_list[1]
    assert output_call[1]["extra"]["output_data_size"] == output_data_size


def test_standard_logger_metadata_in_logs(mock_logger, lambda_context):
    event = {"key": "value"}

    @standard_logger(logger=mock_logger)
    def wrapped_handler(event, context):
        return sample_handler(event, context)

    wrapped_handler(event, lambda_context)

    expected_metadata = {
        "name": lambda_context.function_name,
        "version": lambda_context.function_version,
        "arn": lambda_context.invoked_function_arn,
        "memory_size": lambda_context.memory_limit_in_mb,
        "aws_request_id": lambda_context.aws_request_id,
    }

    # Check metadata in input logging
    input_call = mock_logger.info.call_args_list[0]
    assert input_call[1]["extra"]["lambda_function"] == expected_metadata

    # Check metadata in output logging
    output_call = mock_logger.info.call_args_list[1]
    assert output_call[1]["extra"]["lambda_function"] == expected_metadata
