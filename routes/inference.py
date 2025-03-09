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

    logger.info("Inference endpoint called")

    return {
        "message": "OK",
        "status_code": 200,
    }
