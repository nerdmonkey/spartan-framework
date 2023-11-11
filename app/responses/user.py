from pydantic import BaseModel


class UserResponse(BaseModel):
    id: int
    username: str
    email: str


class UserCreateResponse(BaseModel):
    id: int
    username: str
    email: str


class UserUpdateResponse(BaseModel):
    id: int
    username: str
    email: str
