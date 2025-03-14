# handlers/predict.py
from typing import Dict, Any
from app.helpers.logger import get_logger

logger = get_logger("spartan-framework")

def main(event: Dict[str, Any], context: Any) -> Dict[str, Any]:

    # Log the event and context
    logger.info("Event", extra={"event": event, "context": context.__dict__})

    # Add the missing log message
    logger.info("Predicting...")

    return {
        "statusCode": 200,
        "body": "Hello World"
    }
