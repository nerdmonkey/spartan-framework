from fastapi import APIRouter

from app.helpers.logger import get_logger

logger = get_logger("spartan-framework")


route = APIRouter(
    prefix="/api",
    tags=["Health"],
    responses={404: {"description": "Not found"}},
)


@route.get("/health", response_model=dict)
async def health():
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
