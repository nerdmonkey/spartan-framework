from app.services.logging import StandardLoggerService

standard_logger = StandardLoggerService()


def standard_logging_middleware(handler):
    def wrapper(event, context):
        if not hasattr(context, "cold_start"):
            context.cold_start = True
        else:
            context.cold_start = False

        buffer = {
            "name": context.function_name,
            "version": context.function_version,
            "arn": context.invoked_function_arn,
            "memory_size": context.memory_limit_in_mb,
            "aws_request_id": context.aws_request_id,
            "cold_start": context.cold_start,
        }

        standard_logger.info("Input Data", input_data=event, lambda_function=buffer)

        response = handler(event, context)

        standard_logger.info("Output Data", output_data=response)

        return response

    return wrapper
