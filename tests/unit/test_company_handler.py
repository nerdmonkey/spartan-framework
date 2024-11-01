from unittest.mock import patch

import pytest

from handlers.company import main


@pytest.fixture
def mock_event():
    return {"key": "value"}


@pytest.fixture
def mock_context():
    class Context:
        memory_limit_in_mb = 512
        invoked_function_arn = (
            "arn:aws:lambda:us-west-2:123456789012:function:test_lambda_function"
        )
        aws_request_id = "mock_aws_request_id"
        log_group_name = "/aws/lambda/test_lambda_function"
        log_stream_name = "2024/10/20/[$LATEST]mock_log_stream"
        function_version = "$LATEST"
        function_name = "test_lambda_function"

    return Context()


def test_main_logging_with_mocked_logger(mock_event, mock_context):
    with patch("handlers.company.logger") as mock_logger:
        response = main(mock_event, mock_context)

        assert response == {
            "statusCode": 200,
            "body": "Company lambda executed successfully!",
        }

        mock_logger.debug.assert_called_once_with(
            "Debug message: Company details fetched."
        )
        mock_logger.info.assert_any_call("Info message: Company logged in.")
        mock_logger.warning.assert_called_once_with(
            "Warning message: Company account nearing expiration."
        )
        mock_logger.error.assert_called_once_with(
            "Error message: Failed to update company details."
        )
        mock_logger.critical.assert_called_once_with(
            "Critical message: System failure!"
        )
