from app.helpers.logger import get_logger
from app.helpers.environment import env

import json

def standard_logger(handler, logger=None):
    logger = logger or get_logger("spartan-framework")

    def wrapped_handler(event, context):
        lambda_function = {
            "name": context.function_name,
            "version": context.function_version,
            "arn": context.invoked_function_arn,
            "memory_size": context.memory_limit_in_mb,
            "aws_request_id": context.aws_request_id,
        }
        try:
            input_data_size = len(str(event).encode("utf-8"))
            logger.info(
                "Input Data",
                extra={
                    "input_data": event,
                    "input_data_size": input_data_size,
                    "lambda_function": lambda_function,
                },
            )

            if env("APP_ENVIRONMENT") == "local" and env("APP_DEBUG"):
                print(json.dumps({
                    "input_data": event,
                    "input_data_size": input_data_size,
                    "lambda_function": lambda_function,
                }, indent=4))

            response = handler(event, context)

            output_data_size = len(str(response).encode("utf-8"))
            logger.info(
                "Output Data",
                extra={
                    "output_data": response,
                    "output_data_size": output_data_size,
                    "lambda_function": lambda_function,
                },
            )

            if env("APP_ENVIRONMENT") == "local" and env("APP_DEBUG"):
                print(json.dumps({
                    "output_data": response,
                    "output_data_size": output_data_size,
                    "lambda_function": lambda_function,
                }, indent=4))

            return response

        except Exception as e:
            logger.error("Error in Lambda function", extra={"error": str(e), "lambda_function": lambda_function})
            raise

    return wrapped_handler
