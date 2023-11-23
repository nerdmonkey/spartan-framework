from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.user import User
from app.requests.user import UserCreateRequest, UserUpdateRequest
from app.responses.user import UserCreateResponse, UserResponse, UserUpdateResponse
from sqlalchemy.exc import DatabaseError

class UserService:
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_id(self, user_id: int) -> User:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    def get_users(
        self, page: int, items_per_page: int
    ) -> List[UserResponse]:
        try:
            offset = (page - 1) * items_per_page
            users = self.db.query(User).offset(offset).limit(items_per_page).all()
            user_responses = [
                UserResponse(id=user.id, username=user.username, email=user.email)
                for user in users
            ]
            return user_responses
        except DatabaseError as e:
            raise HTTPException(status_code=500, detail="Internal server error")
        except Exception as e:
            raise HTTPException(status_code=500, detail="Internal server error")

    def get_user(self, user_id: int) -> UserResponse:
        user = self.get_user_by_id(user_id)
        return UserResponse(id=user.id, username=user.username, email=user.email)

    def create_user(self, user: UserCreateRequest) -> UserCreateResponse:
        existing_user = self.db.query(User).filter(User.email == user.email).first()
        if existing_user:
            raise HTTPException(
                status_code=422, detail="User with this email already exists"
            )
        hashed_password = "hashed_" + user.password
        db_user = User(username=user.username, email=user.email, password=hashed_password)
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        response_data = {
            "id": db_user.id,
            "username": db_user.username,
            "email": db_user.email,
        }
        return response_data

    def update_user(self, user_id: int, user: UserUpdateRequest) -> UserUpdateResponse:
        db_user = self.get_user_by_id(user_id)
        user_data = user.dict(exclude_unset=True)
        if "password" in user_data:
            user_data["password"] = "hashed_" + user_data["password"]
        for key, value in user_data.items():
            setattr(db_user, key, value)
        self.db.commit()
        self.db.refresh(db_user)
        response_data = {
            "id": db_user.id,
            "username": db_user.username,
            "email": db_user.email,
        }
        return response_data

    def delete_user(self, user_id: int):
        db_user = self.get_user_by_id(user_id)
        self.db.delete(db_user)
        self.db.commit()
