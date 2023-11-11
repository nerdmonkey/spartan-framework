from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.models.user import User
from app.requests.user import UserCreateRequest, UserUpdateRequest
from app.responses.user import UserCreateResponse, UserResponse, UserUpdateResponse
from config.database import get_session
from sqlalchemy.exc import DatabaseError

route = APIRouter(
    prefix="/api", tags=["Users"], responses={404: {"description": "Not found"}}
)


def get_user_by_id(user_id: int, db: Session) -> User:
    """
    Get a user by their unique identifier.

    Args:
        user_id (int): The unique identifier of the user.
        db (Session): SQLAlchemy database session.

    Returns:
        User: The user object if found.

    Raises:
        HTTPException: If the user with the given ID is not found.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@route.get("/users", status_code=200, response_model=List[UserResponse])
async def get_users(
    page: Optional[int] = Query(1, description="Page number", gt=0),
    items_per_page: Optional[int] = Query(10, description="Items per page", gt=0),
    db: Session = Depends(get_session),
):
    try:
        offset = (page - 1) * items_per_page
        users = db.query(User).offset(offset).limit(items_per_page).all()
        user_responses = [
            UserResponse(id=user.id, username=user.username, email=user.email)
            for user in users
        ]
        return user_responses
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail="Internal server error")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@route.get("/users/{user_id}", status_code=200, response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_session)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse(id=user.id, username=user.username, email=user.email)


@route.post("/users", status_code=201, response_model=UserCreateResponse)
async def create_user(user: UserCreateRequest, db: Session = Depends(get_session)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=422, detail="User with this email already exists"
        )
    hashed_password = "hashed_" + user.password
    db_user = User(username=user.username, email=user.email, password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    response_data = {
        "id": db_user.id,
        "username": db_user.username,
        "email": db_user.email,
    }
    return response_data


@route.put("/users/{user_id}", status_code=200, response_model=UserUpdateResponse)
async def update_user(
    user_id: int, user: UserUpdateRequest, db: Session = Depends(get_session)
):
    db_user = get_user_by_id(user_id, db)
    user_data = user.dict(exclude_unset=True)
    if "password" in user_data:
        user_data["password"] = "hashed_" + user_data["password"]
    for key, value in user_data.items():
        setattr(db_user, key, value)
    db.commit()
    db.refresh(db_user)
    response_data = {
        "id": db_user.id,
        "username": db_user.username,
        "email": db_user.email,
    }
    return response_data


@route.delete("/users/{user_id}", status_code=204)
async def delete_user(user_id: int, db: Session = Depends(get_session)):
    db_user = get_user_by_id(user_id, db)
    db.delete(db_user)
    db.commit()
    return {"ok": True}
