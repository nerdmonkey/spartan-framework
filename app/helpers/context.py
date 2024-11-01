class MockLambdaContext:
    def __init__(self):
        self.function_name = "mock_function_name"
        self.function_version = "$LATEST"
        self.invoked_function_arn = (
            "arn:aws:lambda:us-west-2:123456789012:function:mock_function"
        )
        self.memory_limit_in_mb = 512
        self.aws_request_id = "mock_aws_request_id"
        self.log_group_name = "/aws/lambda/mock_function_name"
        self.log_stream_name = "2024/10/20/[$LATEST]mock_log_stream"

    def get_remaining_time_in_millis(self) -> int:
        return 300000


class MockLambdaEvent:
    def __init__(self):
        self.event = {
            "key1": "value1",
            "key2": "value2",
            "key3": "value3",
        }
