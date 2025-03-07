from app.helpers.logger import get_logger
from app.middlewares.logging import standard_logger

logger = get_logger("spartan-predict")


@standard_logger
def main(event, context):
    logger.info("Predicting...")
    logger.info("Event", extra={
        "event": event,
        "context": context
    })
    return {
        "statusCode": 200,
        "body": "Hello World"
    }
