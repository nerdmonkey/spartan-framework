from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.user import User
from app.requests.user import UserCreateRequest, UserEditRequest
from config.database import get_session
from pydantic import BaseModel
from typing import List

route = APIRouter(
    prefix="/api",
    tags=["Users"],
    responses={404: {"description": "Not found"}}
)

class UserResponse(BaseModel):
    id: int
    username: str
    email: str

class UserCreateResponse(BaseModel):
    id: int
    username: str
    email: str

class UserUpdateResponse(BaseModel):
    id: int
    username: str
    email: str

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
async def get_users(db: Session = Depends(get_session)):
    users = db.query(User).all()

    # Create a list of UserResponse objects from the database results
    user_responses = [
        UserResponse(id=user.id, username=user.username, email=user.email)
        for user in users
    ]

    return user_responses

@route.get("/users/{user_id}", status_code=200, response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_session)):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserResponse(id=user.id, username=user.username, email=user.email)


@route.post("/users", status_code=201, response_model=UserCreateResponse)
async def create_user(user: UserCreateRequest, db: Session = Depends(get_session)):
    # Check if a user with the same email already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this email already exists")

    # TODO: Add password hashing logic here
    hashed_password = "hashed_" + user.password
    db_user = User(username=user.username, email=user.email, password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Construct a dictionary that matches the UserCreateResponse model
    response_data = {
        "id": db_user.id,
        "username": db_user.username,
        "email": db_user.email,
    }

    return response_data


@route.put("/users/{user_id}", status_code=200, response_model=UserUpdateResponse)
async def update_user(user_id: int, user: UserEditRequest, db: Session = Depends(get_session)):
    db_user = get_user_by_id(user_id, db)
    user_data = user.dict(exclude_unset=True)
    # TODO: Add password hashing logic here if password is being updated
    if "password" in user_data:
        user_data["password"] = "hashed_" + user_data["password"]
    for key, value in user_data.items():
        setattr(db_user, key, value)
    db.commit()
    db.refresh(db_user)

    # Construct a dictionary that matches the UserUpdateResponse model
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
