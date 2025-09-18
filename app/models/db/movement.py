from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, Text, func
from sqlalchemy.orm import relationship

from .base import Base


class MovementType(str, Enum):
    put = "put"
    take = "take"
    hold = "hold"


class Movement(Base):
    """
    Database model for Movement.

    Attributes:
        id (int): The primary key for the Movement table.
        username (str): The unique username of the user.
        email (str): The unique email address of the user.
        password (str): The hashed password of the user.
    """

    __tablename__ = "dev_nuriko_movements"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    stock_id = Column(Integer, ForeignKey("dev_nuriko_stocks.id"))
    before = Column(Integer, default=0)
    after = Column(Integer, default=0)
    cost = Column(Integer, default=0)
    reason = Column(Text, nullable=True)
    type = Column(Integer)
    created_at = Column(
        DateTime, nullable=False, default=func.current_timestamp()
    )
    updated_at = Column(
        DateTime, nullable=False, default=func.current_timestamp()
    )

    stock = relationship("Stock", back_populates="movements")
    user = relationship("User", back_populates="movements")
