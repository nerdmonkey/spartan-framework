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
    Handles the inference endpoint.

    Logs the call to the inference endpoint and returns a JSON response
    indicating success.

    Returns:
        dict: A dictionary containing a message and a status code.
    """

    logger.info("Inference endpoint called")

    return {
        "message": "OK",
        "status_code": 200,
    }
