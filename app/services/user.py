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

    def get_by_id(self, id: int) -> User:
        user = self.db.query(User).filter(User.id == id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    def all(
        self, page: int, items_per_page: int
    ) -> List[UserResponse]:
        try:
            offset = (page - 1) * items_per_page
            users = self.db.query(User).offset(offset).limit(items_per_page).all()
            responses = [
                UserResponse(id=user.id, username=user.username, email=user.email)
                for user in users
            ]
            return responses
        except DatabaseError as e:
            raise HTTPException(status_code=500, detail="Internal server error")
        except Exception as e:
            raise HTTPException(status_code=500, detail="Internal server error")

    def find(self, id: int) -> UserResponse:
        user = self.get_by_id(id)
        return UserResponse(id=user.id, username=user.username, email=user.email)

    def save(self, user: UserCreateRequest) -> UserCreateResponse:
        existing = self.db.query(User).filter(User.email == user.email).first()
        if existing:
            raise HTTPException(
                status_code=422, detail="User with this email already exists"
            )
        hashed_password = "hashed_" + user.password
        db = User(username=user.username, email=user.email, password=hashed_password)
        self.db.add(db)
        self.db.commit()
        self.db.refresh(db)
        response_data = {
            "id": db.id,
            "username": db.username,
            "email": db.email,
        }
        return response_data

    def update(self, id: int, user: UserUpdateRequest) -> UserUpdateResponse:
        db = self.get_by_id(id)
        data = user.dict(exclude_unset=True)
        if "password" in data:
            data["password"] = "hashed_" + data["password"]
        for key, value in data.items():
            setattr(db, key, value)
        self.db.commit()
        self.db.refresh(db)
        response_data = {
            "id": db.id,
            "username": db.username,
            "email": db.email,
        }
        return response_data

    def delete(self, id: int):
        db = self.get_by_id(id)
        self.db.delete(db)
        self.db.commit()
        response_data = {
            "id": db.id,
            "username": db.username,
            "email": db.email,
        }
        return response_data
