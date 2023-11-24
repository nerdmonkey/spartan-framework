from pydantic import BaseModel, validator, EmailStr
from typing import Optional
from app.models.user import User
from config.database import get_session

db = get_session()

class UserCreateRequest(BaseModel):
    username: str
    email: EmailStr
    password: str

    @validator('email')
    def email_must_be_unique(cls, v):
        if cls.is_email_exist(v, db):
            raise ValueError('Email already in use')
        return v

    def is_email_exist(email: str, session: db) -> bool:
        return session.query(User).filter(User.email == email).first() is not None

class UserUpdateRequest(UserCreateRequest):
    @validator('email')
    def email_must_be_unique(cls, v, values, **kwargs):
        # Assuming you have access to the user's ID or some unique identifier here
        user_id = values.get('user_id')  # Replace 'user_id' with the actual field name
        if cls.is_email_exist(v, db):
            raise ValueError('Email already in use')
        return v
