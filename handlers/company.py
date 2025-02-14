# handlers/company.py
import json
import os
from datetime import datetime
from typing import Any, Dict

from aws_lambda_powertools.utilities.parser import ValidationError, parse
from aws_lambda_powertools.utilities.typing import LambdaContext

from app.helpers.logger.factory import LoggerFactory

# Initialize logger
logger = LoggerFactory.create_logger(
    service_name="spartan-framework", level=os.getenv("LOG_LEVEL", "INFO")
)

# JSON Schema for request validation
company_schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string", "minLength": 1},
        "industry": {"type": "string"},
        "employees": {"type": "integer", "minimum": 1},
        "active": {"type": "boolean"},
        "founded_date": {"type": "string", "format": "date"},
    },
    "required": ["name", "industry", "employees"],
}


class CompanyError(Exception):
    def __init__(self, message: str, error_code: str):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


def create_error_response(
    status_code: int, message: str, error_code: str
) -> Dict:
    return {
        "statusCode": status_code,
        "body": json.dumps({"error": {"code": error_code, "message": message}}),
        "headers": {"Content-Type": "application/json"},
    }


def process_company_data(company_data: Dict[str, Any]) -> Dict[str, Any]:
    """Process company data and perform business logic"""
    logger.debug(
        "Processing company data",
        extra={
            "company_name": company_data.get("name"),
            "industry": company_data.get("industry"),
        },
    )

    # Simulate business logic
    if company_data.get("employees", 0) > 10000:
        logger.warning(
            "Large company detected - requiring additional validation",
            extra={
                "company_name": company_data.get("name"),
                "employee_count": company_data.get("employees"),
            },
        )
        # Additional validation logic here

    # Simulate database operation
    company_id = f"comp_{int(datetime.utcnow().timestamp())}"

    logger.info(
        "Company record created",
        extra={
            "company_id": company_id,
            "company_name": company_data.get("name"),
        },
    )

    return {
        "company_id": company_id,
        "name": company_data.get("name"),
        "status": "ACTIVE",
        "created_at": datetime.utcnow().isoformat(),
    }


@logger.inject_lambda_context
def main(
    event: Dict[str, Any], context: LambdaContext = None
) -> Dict[str, Any]:
    """
    Lambda handler for company creation
    """
    try:
        # Extract request context
        request_context = event.get("requestContext", {})
        request_id = request_context.get("requestId", "N/A")

        # Log initial request
        logger.info(
            "Received company creation request",
            extra={
                "request_id": request_id,
                "path": event.get("path"),
                "http_method": event.get("httpMethod"),
                "remaining_time": context.get_remaining_time_in_millis(),
            },
        )

        # Parse and validate request body
        try:
            body = json.loads(event.get("body", "{}"))
            logger.debug("Request body parsed", extra={"body": body})
        except json.JSONDecodeError as e:
            logger.error(
                "Invalid JSON in request body",
                extra={"error": str(e), "raw_body": event.get("body")},
            )
            return create_error_response(
                400, "Invalid JSON payload", "INVALID_JSON"
            )

        # Validate against schema
        try:
            validate_input(event=body, schema=company_schema)
            logger.debug("Request validation successful")
        except Exception as e:
            logger.warning(
                "Validation failed for company data",
                extra={"validation_error": str(e), "body": body},
            )
            return create_error_response(400, str(e), "VALIDATION_ERROR")

        # Process company data
        try:
            result = process_company_data(body)
        except CompanyError as e:
            logger.error(
                "Business logic error",
                extra={
                    "error_code": e.error_code,
                    "error_message": e.message,
                    "company_data": body,
                },
            )
            return create_error_response(400, e.message, e.error_code)
        except Exception as e:
            logger.exception(
                "Unexpected error in business logic",
                extra={"error_type": type(e).__name__, "company_data": body},
            )
            return create_error_response(
                500, "Internal server error", "INTERNAL_ERROR"
            )

        # Log successful completion
        logger.info(
            "Company creation completed successfully",
            extra={
                "company_id": result["company_id"],
                "processing_time_ms": context.get_remaining_time_in_millis(),
            },
        )

        return {
            "statusCode": 201,
            "body": json.dumps(result),
            "headers": {
                "Content-Type": "application/json",
                "X-Request-ID": request_id,
            },
        }

    except Exception as e:
        logger.exception(
            "Unhandled exception in lambda handler",
            extra={"error_type": type(e).__name__, "request_id": request_id},
        )
        return create_error_response(
            500, "Internal server error", "UNHANDLED_ERROR"
        )
