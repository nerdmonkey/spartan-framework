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

class UserUpdateRequest(BaseModel):
    username: Optional[str]
    email: Optional[EmailStr]
    password: Optional[str]

    @classmethod
    def is_email_exist(cls, email: str, user_id: int, db: db) -> bool:
        return db.query(User).filter(User.email == email, User.id != user_id).first() is not None

    @validator('email')
    def email_must_be_unique(cls, v, values, **kwargs):
        db = kwargs.get('db')
        user_id = kwargs.get('user_id')
        if v and db and user_id and cls.is_email_exist(v, user_id, db):
            raise ValueError('Email already in use')
        return v
