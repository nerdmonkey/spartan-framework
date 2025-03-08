# handlers/predict.py
from typing import Dict, Any
from aws_lambda_powertools import Logger

logger = Logger()

def get_logger():
    return logger

def main(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    logger = get_logger()

    # Log the event and context
    logger.info("Event", extra={"event": event, "context": context.__dict__})

    # Add the missing log message
    logger.info("Predicting...")

    return {
        "statusCode": 200,
        "body": "Hello World"
    }
