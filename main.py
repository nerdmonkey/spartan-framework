from handlers.inference import main as inference_main

def main(event, context):
    """Entry point for Google Cloud Functions."""
    return inference_main(event, context)


if __name__ == "__main__":
    from app.helpers.context import MockLambdaContext, MockLambdaEvent
    from app.helpers.logger import get_logger

    logger = get_logger("spartan.inference")

    event = MockLambdaEvent()
    context = MockLambdaContext()

    try:
        logger.info("Handler Response", extra={"response": inference_main(event, context)})
    except Exception as e:
        logger.exception("Unhandled exception in main", extra={"error": str(e)})
