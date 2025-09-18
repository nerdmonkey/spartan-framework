"""
Error response models following convention patterns.

This module defines error response formats that align with GitHub Copilot
conventions for consistent error handling across the application.
"""

import uuid
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """
    Standard error response format following convention.

    All API errors should use this format for consistency.

    Fields:
        status_code: HTTP status code
        error: Error type/category
        message: Human-readable error message
        fields: Field-specific error details (for validation errors)
        request_id: Unique request identifier for tracking
    """

    status_code: int
    error: str
    message: str
    fields: Optional[Dict[str, Any]] = Field(default_factory=dict)
    request_id: str = Field(
        default_factory=lambda: f"req_{uuid.uuid4().hex[:8]}"
    )


class ValidationErrorResponse(ErrorResponse):
    """Validation error response for 422 status codes."""

    status_code: int = 422
    error: str = "ValidationError"


class AuthenticationErrorResponse(ErrorResponse):
    """Authentication error response for 401 status codes."""

    status_code: int = 401
    error: str = "AuthenticationError"


class AuthorizationErrorResponse(ErrorResponse):
    """Authorization error response for 403 status codes."""

    status_code: int = 403
    error: str = "AuthorizationError"


class NotFoundErrorResponse(ErrorResponse):
    """Not found error response for 404 status codes."""

    status_code: int = 404
    error: str = "NotFoundError"


class ConflictErrorResponse(ErrorResponse):
    """Conflict error response for 409 status codes."""

    status_code: int = 409
    error: str = "ConflictError"


class RateLimitErrorResponse(ErrorResponse):
    """Rate limit error response for 429 status codes."""

    status_code: int = 429
    error: str = "RateLimitError"


class InternalServerErrorResponse(ErrorResponse):
    """Internal server error response for 500 status codes."""

    status_code: int = 500
    error: str = "InternalServerError"


# Convenience functions for creating error responses
def create_auth_error(
    message: str = "Authentication required",
) -> ErrorResponse:
    """Create authentication error following convention."""
    return AuthenticationErrorResponse(message=message)


def create_forbidden_error(
    message: str = "Insufficient permissions",
) -> ErrorResponse:
    """Create authorization error following convention."""
    return AuthorizationErrorResponse(message=message)


def create_validation_error(
    message: str, fields: Optional[Dict[str, Any]] = None
) -> ErrorResponse:
    """Create validation error following convention."""
    return ValidationErrorResponse(message=message, fields=fields or {})


def create_not_found_error(
    message: str = "Resource not found",
) -> ErrorResponse:
    """Create not found error following convention."""
    return NotFoundErrorResponse(message=message)


def create_rate_limit_error(
    message: str = "Rate limit exceeded",
) -> ErrorResponse:
    """Create rate limit error following convention."""
    return RateLimitErrorResponse(message=message)
