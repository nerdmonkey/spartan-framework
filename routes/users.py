from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.requests.user import UserCreateRequest, UserUpdateRequest
from app.responses.user import UserCreateResponse, UserResponse, UserUpdateResponse
from config.database import get_session
from sqlalchemy.exc import DatabaseError
from app.services.user import UserService


# Create an instance of the UserService and use it in the API endpoints
user_service = UserService(db=None)  # Pass the database session as needed

route = APIRouter(
    prefix="/api", tags=["Users"], responses={404: {"description": "Not found"}}
)

@route.get("/users", status_code=200, response_model=List[UserResponse])
async def get_users(
    page: Optional[int] = Query(1, description="Page number", gt=0),
    items_per_page: Optional[int] = Query(10, description="Items per page", gt=0),
    db: Session = Depends(get_session),
):
    user_service.db = db
    return user_service.get_users(page, items_per_page)

@route.get("/users/{user_id}", status_code=200, response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_session)):
    user_service.db = db
    return user_service.get_user(user_id)

@route.post("/users", status_code=201, response_model=UserCreateResponse)
async def create_user(user: UserCreateRequest, db: Session = Depends(get_session)):
    user_service.db = db
    return user_service.create_user(user)

@route.put("/users/{user_id}", status_code=200, response_model=UserUpdateResponse)
async def update_user(
    user_id: int, user: UserUpdateRequest, db: Session = Depends(get_session)
):
    user_service.db = db
    return user_service.update_user(user_id, user)

@route.delete("/users/{user_id}", status_code=204)
async def delete_user(user_id: int, db: Session = Depends(get_session)):
    user_service.db = db
    user_service.delete_user(user_id)
    return {"ok": True}
