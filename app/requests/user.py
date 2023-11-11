from pydantic import BaseModel

class UserCreateRequest(BaseModel):
    """
    Pydantic model representing a request for creating a User.

    Attributes:
        username (str): The username of the user.
        email (str): The email address of the user.
        password (str): The password of the user.
    """

    username: str
    email: str
    password: str

class UserUpdateRequest(UserCreateRequest):
    """
    Pydantic model representing a request for updating a User.

    Attributes:
        username (str): The updated username of the user.
        email (str): The updated email address of the user.
        password (str): The updated password of the user.
    """

    username: str
    email: str
    password: str
