from typing import List
from pydantic import BaseModel


class UserResponse(BaseModel):
    id: int
    username: str
    email: str

class Pagination(BaseModel):
    page: int
    items_per_page: int
    total_items: int

class PaginatedUserResponse(BaseModel):
    users: List[UserResponse]
    pagination: Pagination

class UserCreateResponse(BaseModel):
    """
    Pydantic model representing a response for creating a User.

    Attributes:
        id (int): The unique identifier of the created user.
        username (str): The username of the created user.
        email (str): The email address of the created user.
    """

    id: int
    username: str
    email: str


class UserUpdateResponse(BaseModel):
    """
    Pydantic model representing a response for updating a User.

    Attributes:
        id (int): The unique identifier of the updated user.
        username (str): The updated username of the user.
        email (str): The updated email address of the user.
    """

    id: int
    username: str
    email: str
