from typing import Any, Dict

from app.helpers.logger import get_logger


logger = get_logger("spartan.inference")


def main(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    logger.info(
        f"Event: {event}, Context: {getattr(context, '__dict__', str(context))}"
    )

    # Test PII sanitization in CloudWatch
    logger.info("Testing PII sanitization", extra={
        "username": "test_user",
        "password": "super_secret_password",
        "api_key": "sk-1234567890abcdef",
        "token": "jwt_token_here",
        "secret": "should_be_redacted",
        "normal_field": "this_should_appear"
    })

    # Test environment metadata
    logger.info("Testing environment metadata inclusion")

    # Test log sampling with multiple messages (30% sample rate)
    for i in range(10):
        logger.info(f"Batch log message {i+1} - testing 30% sampling rate")

    logger.info("This is an info message")
    logger.debug("This is a debug message")
    logger.error(
        "This is an error message",
        extra={
            "error_code": 500,
            "details": "An error occurred",
            "credentials": "should_be_redacted"
        },
    )
    logger.warning("This is a warning message")

    return {"statusCode": 200, "body": "Hello Spartan!"}


if __name__ == "__main__":
    from app.helpers.context import MockLambdaContext, MockLambdaEvent

    event = MockLambdaEvent()
    context = MockLambdaContext()

    try:
        logger.info(
            "Handler Response", extra={"response": main(event, context)}
        )
    except Exception as e:
        logger.exception("Unhandled exception in main", extra={"error": str(e)})
