from typing import List, Tuple, Union

from sqlalchemy.exc import DatabaseError
from sqlalchemy.orm import Session

from app.exceptions.database import DatabaseInternalError
from app.exceptions.user import (
    DuplicateUserError,
    InvalidSortFieldError,
    UserNotFoundError,
)
from app.models.user import User
from app.requests.user import UserCreateRequest, UserUpdateRequest
from app.responses.user import UserCreateResponse, UserResponse, UserUpdateResponse


class UserService:
    """
    Service class for managing user-related operations.
    """

    def __init__(self, db: Session):
        """
        Initialize the UserService class.

        Args:
            db (Session): The database session.
        """
        self.db = db

    def get_by_id(self, id: int) -> User:
        """
        Retrieve a user by their ID.

        Args:
            id (int): The ID of the user.

        Returns:
            User: The user object.

        Raises:
            UserNotFoundError: If the user is not found.
        """
        user = self.db.query(User).filter_by_field("id", id).first()
        if not user:
            raise UserNotFoundError("User not found")
        return user

    def all(
        self,
        page: int,
        items_per_page: int,
        sort_type: str = "asc",
        sort_by: str = "id",
        start_date: str = None,
        end_date: str = None,
        username: str = None,
        email: str = None,
    ) -> Tuple[List[UserResponse], int, int, int, int]:
        """
        Retrieve all users with pagination and optional filters.

        Args:
            page (int): The page number.
            items_per_page (int): The number of items per page.
            sort_type (str): The sort type ('asc' or 'desc').
            sort_by (str): The field to sort by.
            start_date (str): The start date for the filter (YYYY-MM-DD).
            end_date (str): The end date for the filter (YYYY-MM-DD).
            username (str): The username filter.
            email (str): The email filter.

        Returns:
            Tuple: A tuple containing the list of user responses and pagination info.

        Raises:
            InvalidSortFieldError: If the sort field is invalid.
        """
        offset = (page - 1) * items_per_page

        # Sort handling
        descending = sort_type == "desc"
        valid_sort_fields = ["id", "username", "email", "created_at", "updated_at"]
        if sort_by not in valid_sort_fields:
            raise InvalidSortFieldError("Invalid sort_by field")
        self.db.order_by(sort_by, descending=descending)

        # Apply filters
        if start_date and end_date:
            self.db.filter_by_date_range("created_at", start_date, end_date)
        if username:
            self.db.filter_by_field("username", username)
        if email:
            self.db.filter_by_field("email", email)

        # Retrieve filtered and paginated results
        users = self.db.offset(offset).limit(items_per_page).all()
        total_users = self.db.count()
        last_page = (total_users - 1) // items_per_page + 1
        first_item = offset + 1
        last_item = min(offset + items_per_page, total_users)

        # Convert users to response format
        responses = [
            UserResponse(
                id=user.id,
                username=user.username,
                email=user.email,
                created_at=user.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                updated_at=user.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
            )
            for user in users
        ]

        return responses, total_users, last_page, first_item, last_item

    def save(self, user_request: UserCreateRequest) -> UserCreateResponse:
        """
        Save a new user to the database.

        Args:
            user_request (UserCreateRequest): The user create request object.

        Returns:
            UserCreateResponse: The response data of the created user.

        Raises:
            DuplicateUserError: If a user with the same email already exists.
        """
        existing_user = (
            self.db.query(User).filter_by_field("email", user_request.email).first()
        )
        if existing_user:
            raise DuplicateUserError("User with this email already exists")

        user_data = user_request.model_dump(exclude_unset=True)
        user_data["password"] = "hashed_" + user_data["password"]
        new_user = User(**user_data)

        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)

        return UserCreateResponse(
            id=new_user.id,
            username=new_user.username,
            email=new_user.email,
            created_at=new_user.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            updated_at=new_user.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
        )

    def update(self, id: int, user_request: UserUpdateRequest) -> UserUpdateResponse:
        """
        Update a user in the database.

        Args:
            id (int): The ID of the user.
            user_request (UserUpdateRequest): The user update request object.

        Returns:
            UserUpdateResponse: The response data of the updated user.

        Raises:
            UserNotFoundError: If the user is not found.
        """
        user = self.get_by_id(id)
        update_data = user_request.model_dump(exclude_unset=True)
        if "password" in update_data:
            update_data["password"] = "hashed_" + update_data["password"]

        for key, value in update_data.items():
            setattr(user, key, value)

        self.db.commit()
        self.db.refresh(user)

        return UserUpdateResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            created_at=user.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            updated_at=user.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
        )

    def delete(self, id: int) -> UserResponse:
        """
        Delete a user by ID.

        Args:
            id (int): The ID of the user to delete.

        Returns:
            UserResponse: The deleted user information.

        Raises:
            UserNotFoundError: If the user is not found.
        """
        user = self.get_by_id(id)

        response = UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            created_at=user.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            updated_at=user.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
        )

        self.db.delete(user)
        self.db.commit()

        return response

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
            UserNotFoundError: If the user is not found.
        """
        user = self.get_by_id(id)
        return UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            created_at=user.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            updated_at=user.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
        )
