from sqlalchemy import Column, Integer, String
from .base import Base


class User(Base):
    """
    Database model for User.

    Attributes:
        id (int): The primary key for the User table.
        username (str): The unique username of the user.
        email (str): The unique email address of the user.
        password (str): The hashed password of the user.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
