import functools
from typing import Any, Callable


def standard_logger(func: Callable = None, *, logger=None) -> Callable:
    """
    A decorator that provides standardized logging for Lambda functions.
    Can be used with or without parameters.

    @standard_logger
    def func(): pass

    or

    @standard_logger(logger=custom_logger)
    def func(): pass
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(event: dict, context: Any) -> Any:
            # Use provided logger or get default logger
            nonlocal logger
            if logger is None:
                from app.helpers.logger import get_logger

                logger = get_logger()

            # Prepare Lambda metadata
            lambda_metadata = {
                "name": context.function_name,
                "version": context.function_version,
                "arn": context.invoked_function_arn,
                "memory_size": context.memory_limit_in_mb,
                "aws_request_id": context.aws_request_id,
            }

            # Calculate input size
            input_data_size = len(str(event).encode("utf-8"))

            try:
                # Log input data
                logger.info(
                    "Lambda function invoked",
                    extra={
                        "input_data": event,
                        "input_data_size": input_data_size,
                        "lambda_function": lambda_metadata,
                    },
                )

                # Execute the function
                response = func(event, context)

                # Calculate output size
                output_data_size = len(str(response).encode("utf-8"))

                # Log successful execution
                logger.info(
                    "Lambda function completed successfully",
                    extra={
                        "output_data": response,
                        "output_data_size": output_data_size,
                        "lambda_function": lambda_metadata,
                    },
                )

                return response

            except Exception as e:
                # Log error details
                error_message = str(e)
                logger.error(
                    "Error in Lambda function",
                    extra={
                        "error": error_message,
                        "lambda_function": lambda_metadata,
                    },
                )
                raise

        return wrapper

    # Handle both @standard_logger and @standard_logger(logger=custom_logger) cases
    if func is None:
        return decorator
    return decorator(func)
