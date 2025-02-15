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
    wrapped_handler = standard_logger(
        sample_handler, logger=mock_logger
    )

    event = {"key": "value"}

    response = wrapped_handler(event, lambda_context)

    print(mock_logger.info.call_args_list)  # Debugging line

    assert any(
        "extra" in call[1] and call[1]["extra"].get("input_data") == event
        for call in mock_logger.info.call_args_list
    ), f"Input data log missing, call_args_list: {mock_logger.info.call_args_list}"

    assert any(
        "extra" in call[1] and call[1]["extra"].get("output_data") == response
        for call in mock_logger.info.call_args_list
    ), f"Output data log missing, call_args_list: {mock_logger.info.call_args_list}"

    assert response == {"statusCode": 200, "body": "Hello, world!"}


def test_standard_logger_logs_error(mock_logger, lambda_context):
    wrapped_handler = standard_logger(
        sample_handler_with_error, logger=mock_logger
    )

    event = {"key": "value"}

    with pytest.raises(ValueError, match="Intentional Error"):
        wrapped_handler(event, lambda_context)

    assert (
        mock_logger.error.called
    ), f"Expected logger.error to be called but it wasn't. Error call_args_list: {mock_logger.error.call_args_list}"
    assert any(
        "Error in Lambda function" in call[0][0]
        and "Intentional Error" in call[1]["extra"]["error"]
        for call in mock_logger.error.call_args_list
    ), "Expected error log with 'Intentional Error' not found"


def test_standard_logger_logs_request_and_response_sizes(mock_logger, lambda_context):
    wrapped_handler = standard_logger(
        sample_handler, logger=mock_logger
    )

    event = {"key": "value" * 100}

    response = wrapped_handler(event, lambda_context)

    input_data_size = len(str(event).encode("utf-8"))
    output_data_size = len(str(response).encode("utf-8"))

    assert any(
        "extra" in call[1] and call[1]["extra"].get("input_data_size") == input_data_size
        for call in mock_logger.info.call_args_list
    ), f"Input data size log missing or incorrect, call_args_list: {mock_logger.info.call_args_list}"
    assert any(
        "extra" in call[1] and call[1]["extra"].get("output_data_size") == output_data_size
        for call in mock_logger.info.call_args_list
    ), f"Output data size log missing or incorrect, call_args_list: {mock_logger.info.call_args_list}"


def test_standard_logger_metadata_in_logs(mock_logger, lambda_context):
    wrapped_handler = standard_logger(
        sample_handler, logger=mock_logger
    )

    event = {"key": "value"}

    wrapped_handler(event, lambda_context)

    lambda_metadata = {
        "name": lambda_context.function_name,
        "version": lambda_context.function_version,
        "arn": lambda_context.invoked_function_arn,
        "memory_size": lambda_context.memory_limit_in_mb,
        "aws_request_id": lambda_context.aws_request_id,
    }

    assert any(
        "extra" in call[1] and call[1]["extra"].get("lambda_function") == lambda_metadata
        for call in mock_logger.info.call_args_list
    ), f"Lambda metadata log missing or incorrect, call_args_list: {mock_logger.info.call_args_list}"
