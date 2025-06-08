# handlers/predict.py
from typing import Dict, Any
from app.helpers.logger import get_logger

logger = get_logger("spartan-framework")


def main(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    # Log the event and context
    logger.info(f"Event: {event}, Context: {getattr(context, '__dict__', str(context))}")

    # Add the missing log message
    logger.info("Predicting...")

    return {
        "statusCode": 200,
        "body": "Hello World"
    }


if __name__ == "__main__":
    from app.helpers.context import MockLambdaContext, MockLambdaEvent

    event = MockLambdaEvent()
    context = MockLambdaContext()

    print(main(event, context))
