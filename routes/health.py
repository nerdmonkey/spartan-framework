from fastapi import APIRouter

route = APIRouter(
    prefix="/api", tags=["Health Check"], responses={404: {"description": "Not found"}}
)


@route.get("/health-check")
async def health_check():
    return {"message": "OK"}
