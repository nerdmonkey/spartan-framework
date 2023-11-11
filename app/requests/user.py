from pydantic import BaseModel


class UserCreateRequest(BaseModel):
    username: str
    email: str
    password: str


class UserUpdateRequest(UserCreateRequest):
    username: str
    email: str
    password: str
