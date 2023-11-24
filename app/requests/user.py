from pydantic import BaseModel, validator, EmailStr
from typing import Optional
from app.models.user import User
from config.database import get_session

db = get_session()

class UserCreateRequest(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserUpdateRequest(BaseModel):
    username: Optional[str]
    email: Optional[EmailStr]
    password: Optional[str]
