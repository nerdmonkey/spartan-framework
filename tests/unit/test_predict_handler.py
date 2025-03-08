from unittest.mock import MagicMock, patch, call

from handlers.predict import main


class Context:
    def __init__(self, **kwargs):
        self.function_name = kwargs.get('function_name', 'test_function')
        self.function_version = kwargs.get('function_version', '$LATEST')
        self.invoked_function_arn = kwargs.get('invoked_function_arn', 'arn:aws:lambda:us-east-1:123456789012:function:test_function')
        self.memory_limit_in_mb = kwargs.get('memory_limit_in_mb', 128)
        self.aws_request_id = kwargs.get('aws_request_id', 'test_request_id')
        self.log_group_name = kwargs.get('log_group_name', '/aws/lambda/test_function')
        self.log_stream_name = kwargs.get('log_stream_name', '2023/12/31/[$LATEST]123456789')
        self.identity = kwargs.get('identity', None)
        self.client_context = kwargs.get('client_context', None)
        self.remaining_time_in_millis = lambda: kwargs.get('remaining_time_in_millis', 300000)


@patch("handlers.predict.get_logger")
def test_main(mock_get_logger):
    # Arrange
    mock_logger = MagicMock()
    mock_get_logger.return_value = mock_logger
    event = {"key": "value"}
    context = Context(
        function_name="test_function",
        aws_request_id="test_request_id",
        function_version="$LATEST"
    )

    # Act
    response = main(event, context)

    # Assert
    assert mock_logger.info.call_count == 2  # Verify two log calls were made

    # Verify the exact calls in order
    expected_calls = [
        call("Event", extra={"event": event, "context": context.__dict__}),
        call("Predicting...")
    ]
    mock_logger.info.assert_has_calls(expected_calls, any_order=False)

    # Verify the response
    assert response == {"statusCode": 200, "body": "Hello World"}
