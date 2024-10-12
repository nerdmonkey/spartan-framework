import pytest

from handlers.main import (
    handle,
)  # Adjust the import according to your project structure


# Test basic function return
def test_handle_success():
    event = {}
    context = {}

    response = handle(event, context)

    # Assert that the function returns the expected statusCode and body
    assert response["statusCode"] == 200
    assert response["body"] == "Hello Spartan!"


# Test handle with different event
def test_handle_with_different_event():
    event = {"key": "value"}  # Mock event object with some random values
    context = {}

    response = handle(event, context)

    # Assert that the function still returns the same statusCode and body regardless of event
    assert response["statusCode"] == 200
    assert response["body"] == "Hello Spartan!"


# Test handle with context simulation
def test_handle_with_context():
    event = {}

    # Mock Lambda context with necessary attributes
    context = {
        "aws_request_id": "test-aws-request-id",
        "log_group_name": "/aws/lambda/test-lambda",
        "log_stream_name": "2023/01/01/[test]abcdef",
        "function_name": "test-lambda-function",
        "memory_limit_in_mb": 128,
        "function_version": "$LATEST",
        "invoked_function_arn": "arn:aws:lambda:us-west-2:123456789012:function:test-lambda-function",
    }

    response = handle(event, context)

    # Assert that the function returns the expected statusCode and body
    assert response["statusCode"] == 200
    assert response["body"] == "Hello Spartan!"
