from fastapi import APIRouter

from app.helpers.logger import get_logger

logger = get_logger("spartan-framework")

route = APIRouter(
    prefix="/api",
    tags=["Inference"],
    responses={404: {"description": "Not found"}},
)

@route.get("/inference", response_model=dict)
async def inference():
    """
    Endpoint for performing inference.

    When accessed, it returns a simple JSON response indicating that the inference service is operational.

    Returns:
        dict: A dictionary with a key 'message' and value 'OK', signifying the service is running.
    """

    logger.info("Inference endpoint called")

    return {
        "message": "OK",
        "status_code": 200,
    }
