from app.services.logging import StandardLoggerService


def standard_logging_middleware(handler, logger=None):
    logger = logger or StandardLoggerService()

    def wrapped_handler(event, context):
        try:
            input_data_size = len(str(event).encode("utf-8"))
            lambda_function = {
                "name": context.function_name,
                "version": context.function_version,
                "arn": context.invoked_function_arn,
                "memory_size": context.memory_limit_in_mb,
                "aws_request_id": context.aws_request_id,
            }
            logger.info(
                "Input Data",
                input_data=event,
                lambda_function=lambda_function,
                input_data_size=input_data_size,
            )

            response = handler(event, context)

            output_data_size = len(str(response).encode("utf-8"))
            logger.info(
                "Output Data", output_data=response, output_data_size=output_data_size
            )
            return response

        except Exception as e:
            logger.error("Error in Lambda function", error=str(e))
            raise

    return wrapped_handler
