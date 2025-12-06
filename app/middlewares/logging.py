"""
Logging middleware for GCP Cloud Functions and Cloud Run.

Automatically detects the GCP platform and extracts appropriate context information.
"""

import json

from app.helpers.environment import env
from app.helpers.logger import get_logger


def _get_function_context(context):
    """
    Extract function context from GCP Cloud Functions or Cloud Run.

    Returns a dict with normalized function metadata.
    """
    function_info = {}

    # Detect GCP Cloud Functions context
    if hasattr(context, "event_id"):
        function_info = {
            "platform": "gcp_cloud_functions",
            "name": env("FUNCTION_NAME", "unknown"),
            "region": env("FUNCTION_REGION", "unknown"),
            "event_id": context.event_id,
            "event_type": context.event_type,
            "request_id": getattr(context, "request_id", None),
        }
    # Detect GCP Cloud Run (Flask request context)
    elif env("K_SERVICE"):
        function_info = {
            "platform": "gcp_cloud_run",
            "service": env("K_SERVICE"),
            "revision": env("K_REVISION", "unknown"),
            "configuration": env("K_CONFIGURATION", "unknown"),
            "region": env("FUNCTION_REGION", "us-central1"),
        }
        # Try to get request ID from context if available
        if hasattr(context, "request_id"):
            function_info["request_id"] = context.request_id
    else:
        # Generic/local context
        function_info = {
            "platform": "generic",
            "environment": env("APP_ENVIRONMENT", "local"),
        }

    return function_info


def standard_logger(handler, logger=None):
    """
    Logging middleware for GCP serverless functions.

    Compatible with:
    - GCP Cloud Functions
    - GCP Cloud Run
    - Local development

    Args:
        handler: The function handler to wrap
        logger: Optional logger instance (defaults to service logger)

    Returns:
        Wrapped handler with logging
    """
    logger = logger or get_logger(env("APP_NAME", "spartan-framework"))

    def wrapped_handler(event, context):
        function_info = _get_function_context(context)

        try:
            input_data_size = len(str(event).encode("utf-8"))
            logger.info(
                "Function invoked",
                extra={
                    "event_type": "function_input",
                    "input_data": event,
                    "input_data_size": input_data_size,
                    "function": function_info,
                },
            )

            if env("APP_ENVIRONMENT") == "local" and env("APP_DEBUG"):
                print(
                    json.dumps(
                        {
                            "event_type": "function_input",
                            "input_data": event,
                            "input_data_size": input_data_size,
                            "function": function_info,
                        },
                        indent=4,
                        default=str,
                    )
                )

            response = handler(event, context)

            output_data_size = len(str(response).encode("utf-8"))
            logger.info(
                "Function completed",
                extra={
                    "event_type": "function_output",
                    "output_data": response,
                    "output_data_size": output_data_size,
                    "function": function_info,
                },
            )

            if env("APP_ENVIRONMENT") == "local" and env("APP_DEBUG"):
                print(
                    json.dumps(
                        {
                            "event_type": "function_output",
                            "output_data": response,
                            "output_data_size": output_data_size,
                            "function": function_info,
                        },
                        indent=4,
                        default=str,
                    )
                )

            return response

        except Exception as e:
            logger.error(
                "Function error",
                extra={
                    "event_type": "function_error",
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "function": function_info,
                },
                exc_info=True,
            )
            raise

    return wrapped_handler
