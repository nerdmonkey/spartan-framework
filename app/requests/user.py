from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator


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

    model_config = ConfigDict(from_attributes=True)

    @field_validator("username", "email", "password")
    def not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("must not be empty")
        return v

    @field_validator("email")
    def valid_email(cls, v):
        if "@" not in v:
            raise ValueError("invalid email format")
        return v


class UserUpdateRequest(BaseModel):
    """
    Data model for updating an existing user.

    Attributes:
        username (Optional[str]): The new username of the user. Optional.
        email (Optional[EmailStr]): The new email address of the user. Optional.
        password (Optional[str]): The new password for the user. Optional.
    """

    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

    @field_validator("username", "email", "password")
    def not_empty(cls, v):
        if v is not None and not v.strip():
            raise ValueError("must not be empty")
        return v

    @field_validator("email")
    def valid_email(cls, v):
        if v is not None and "@" not in v:
            raise ValueError("invalid email format")
        return v
