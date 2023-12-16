from typing import Optional

from pydantic import BaseModel, EmailStr
from datetime import datetime


class UserCreateRequest(BaseModel):
    """
    Data model for creating a new user.

    Attributes:
        username (str): The username of the new user.
        email (EmailStr): The email address of the new user.
        password (str): The password for the new user.
    """

    username: str
    email: EmailStr
    password: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()


class UserUpdateRequest(BaseModel):
    """
    Data model for updating an existing user.

    Attributes:
        username (Optional[str]): The new username of the user. Optional.
        email (Optional[EmailStr]): The new email address of the user. Optional.
        password (Optional[str]): The new password for the user. Optional.
    """

    username: Optional[str]
    email: Optional[EmailStr]
    password: Optional[str]
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
