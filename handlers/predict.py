from typing import Any, Dict

from app.helpers.logger import get_logger

logger = get_logger("spartan-framework")


def main(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    logger = get_logger()

    logger.info("Event", extra={"event": event, "context": context.__dict__})

    logger.info("Predicting...")

    return {"statusCode": 200, "body": "Hello World"}
