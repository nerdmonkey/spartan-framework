from app.middlewares.logging import standard_logging_middleware
from app.services.logging import StandardLoggerService

logger = StandardLoggerService()


@standard_logging_middleware
def main(event, context):
    """
    Main handler function for processing company-related events.

    Logs messages at various levels based on the standard Python logging module hierarchy:
    - DEBUG (10): Detailed information, typically of interest only when diagnosing problems.
    - INFO (20): Confirmation that things are working as expected.
    - WARNING (30): An indication that something unexpected happened, or indicative of some problem in the near future.
    - ERROR (40): Due to a more serious problem, the software has not been able to perform some function.
    - CRITICAL (50): A serious error, indicating that the program itself may be unable to continue running.

    Args:
        event (dict): The event data that triggered the function.
        context (object): The runtime information of the function.

    Returns:
        dict: A response object containing the status code and body message.
    """

    logger.debug(
        "Debug message: Company details fetched."
    )  # Only logged if LOG_LEVEL is DEBUG

    logger.info(
        "Info message: Company logged in."
    )  # Logged when LOG_LEVEL is INFO or lower

    logger.warning(
        "Warning message: Company account nearing expiration."
    )  # Logged if LOG_LEVEL is WARNING or lower

    logger.error(
        "Error message: Failed to update company details."
    )  # Logged if LOG_LEVEL is ERROR or lower

    logger.critical("Critical message: System failure!")  # Always logged

    return {"statusCode": 200, "body": "Company lambda executed successfully!"}
