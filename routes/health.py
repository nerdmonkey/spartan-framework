from fastapi import APIRouter

from app.helpers.logger import get_logger

logger = get_logger("spartan-framework")


route = APIRouter(
    prefix="/api",
    tags=["Health Check"],
    responses={404: {"description": "Not found"}},
)
"""
Defines the routing for the Health Check API.

The APIRouter instance 'route' is configured with a prefix '/api' and a tag 'Health Check'.
It also includes a standard response for 404 errors, indicating that a requested resource was not found.
"""


@route.get("/health", response_model=dict)
async def health_check():
    """
    Endpoint for checking the health of the API service.

    When accessed, it returns a simple JSON response indicating that the service is operational.

    Returns:
        dict: A dictionary with a key 'message' and value 'OK', signifying the service is running.
    """

    logger.info("Health check endpoint called")

    return {
        "message": "OK",
        "status_code": 200,
    }
