from pydantic import ConfigDict
from sqlalchemy import (
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import relationship

from .base import Base


class Profile(Base):
    """
    Represents a user profile.

    Attributes:
        id (int): The unique identifier for the profile.
        user_id (int): The unique identifier for the associated user.
        given_name (str): The given name of the user.
        family_name (str): The family name of the user.
        middle_name (str): The middle name of the user.
        nickname (str): The nickname of the user.
        profile (str): The profile URL of the user.
        picture (str): The profile picture URL of the user.
        website (str): The website URL of the user.
        zoneinfo (str): The time zone information of the user.
        locale (str): The locale of the user.
        gender (int): The gender of the user.
        birthdate (datetime.date): The birthdate of the user.
        address (str): The address of the user.
        created_at (datetime.datetime): The timestamp when the profile was created.
        updated_at (datetime.datetime): The timestamp when the profile was last updated.
    """

    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, index=True)
    given_name = Column(String, nullable=False)
    family_name = Column(String, nullable=False)
    middle_name = Column(String, nullable=False)
    nickname = Column(String, nullable=False)
    profile = Column(String, nullable=False)
    picture = Column(String, nullable=False)
    website = Column(String, nullable=False)
    zoneinfo = Column(String, nullable=False)
    locale = Column(String, nullable=False)
    gender = Column(Integer, nullable=False)
    birthdate = Column(Date, nullable=False)
    address = Column(Text, nullable=False)
    created_at = Column(
        DateTime, nullable=False, default=func.current_timestamp()
    )
    updated_at = Column(
        DateTime, nullable=False, default=func.current_timestamp()
    )

    user = relationship("User", back_populates="profile")

    model_config = ConfigDict(from_attributes=True)
