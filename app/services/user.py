from typing import List

from fastapi import HTTPException
from sqlalchemy.exc import DatabaseError
from sqlalchemy.orm import Session

from app.models.user import User
from app.requests.user import UserCreateRequest, UserUpdateRequest
from app.responses.user import UserCreateResponse, UserResponse, UserUpdateResponse


class UserService:
    """
    Service class for managing user-related operations.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, id: int) -> User:
        """
        Retrieve a user by their ID.

        Args:
            id (int): The ID of the user.

        Returns:
            User: The user object.

        Raises:
            HTTPException: If the user is not found.
        """
        user = self.db.query(User).filter(User.id == id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    def all(self, page: int, items_per_page: int) -> List[UserResponse]:
        try:
            offset = (page - 1) * items_per_page
            users = self.db.query(User).offset(offset).limit(items_per_page).all()
            responses = [
                UserResponse(**user.__dict__) for user in users
            ]

            return responses, self.total()
        except DatabaseError as e:
            raise HTTPException(status_code=500, detail="Internal server error")
        except Exception as e:
            raise HTTPException(status_code=500, detail="Internal server error")

    def total(self) -> int:
        """
        Get the total number of users.

        Returns:
            int: The total number of users.
        """
        return self.db.query(User).count()

    def find(self, id: int) -> UserResponse:
        """
        Find a user by their ID and return the user response.

        Args:
            id (int): The ID of the user.

        Returns:
            UserResponse: The user response.

        Raises:
            HTTPException: If the user is not found.
        """
        user = self.get_by_id(id)
        return UserResponse(id=user.id, username=user.username, email=user.email)

    def save(self, user: UserCreateRequest) -> UserCreateResponse:
        """
        Save a new user to the database.

        Args:
            user (UserCreateRequest): The user create request object.

        Returns:
            UserCreateResponse: The response data of the created user.

        Raises:
            HTTPException: If a user with the same email already exists.
        """
        existing = self.db.query(User).filter(User.email == user.email).first()
        if existing:
            raise HTTPException(
                status_code=422, detail="User with this email already exists"
            )
        hashed_password = "hashed_" + user.password
        item = User(username=user.username, email=user.email, password=hashed_password)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        response_data = {
            "id": item.id,
            "username": item.username,
            "email": item.email,
        }
        return response_data

    def update(self, id: int, user: UserUpdateRequest) -> UserUpdateResponse:
        """
        Update a user in the database.

        Args:
            id (int): The ID of the user.
            user (UserUpdateRequest): The user update request object.

        Returns:
            UserUpdateResponse: The response data of the updated user.
        """
        item = self.get_by_id(id)
        data = user.dict(exclude_unset=True)
        if "password" in data:
            data["password"] = "hashed_" + data["password"]
        for key, value in data.items():
            setattr(item, key, value)
        self.db.commit()
        self.db.refresh(item)
        response_data = {
            "id": item.id,
            "username": item.username,
            "email": item.email,
        }
        return response_data

    def delete(self, id: int):
        """
        Delete a user from the database.

        Args:
            id (int): The ID of the user.

        Returns:
            dict: The response data of the deleted user.
        """
        item = self.get_by_id(id)
        self.db.delete(item)
        self.db.commit()
        response_data = {
            "id": item.id,
            "username": item.username,
            "email": item.email,
        }
        return response_data
