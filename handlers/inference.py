from typing import Any, Dict

from app.helpers.logger import get_logger

logger = get_logger("sample-service")


def main(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    logger.info(
        f"Event: {event}, Context: {getattr(context, '__dict__', str(context))}"
    )

    logger.info("This is an info message")
    logger.debug("This is a debug message")
    logger.error(
        "This is an error message",
        extra={"error_code": 500, "details": "An error occurred"},
    )
    logger.warning("This is a warning message")

    return {"statusCode": 200, "body": "Hello World"}


if __name__ == "__main__":
    from app.helpers.context import MockLambdaContext, MockLambdaEvent

    event = MockLambdaEvent()
    context = MockLambdaContext()

    try:
        print(main(event, context))
    except Exception as e:
        logger.exception("Unhandled exception in main", extra={"error": str(e)})
