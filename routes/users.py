from fastapi import APIRouter, Depends, Security
from config.database import Session, engine, get_session
from app.models.user import User


def get_db():
    try:
        db = Session()
        yield db
    finally:
        db.close()


route = APIRouter(
    prefix="/api",
    tags=["Users"],
    responses={404: {"description": "Not found"}}
)

@route.get("/users",status_code=200)
async def get_users(db: Session = Depends(get_db)):

    users_data = db.query(User).all()

    return {
        "data": users_data
    }
