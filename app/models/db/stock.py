from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from app.models.db.movement import Movement

from .base import Base


class Stock(Base):
    """
    Database model for Stock.

    Attributes:
        id (int): The primary key for the Stock table.
        username (str): The unique username of the user.
        email (str): The unique email address of the user.
        password (str): The hashed password of the user.
    """

    __tablename__ = "dev_nuriko_stocks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    inventory_id = Column(Integer, ForeignKey("dev_nuriko_inventories.id"))
    supplier_id = Column(Integer, ForeignKey("dev_nuriko_suppliers.id"))
    location_id = Column(Integer, ForeignKey("dev_nuriko_locations.id"))
    quantity = Column(Integer, default=0)
    selling_price = Column(Integer, default=0)
    original_price = Column(Integer, default=0)
    markup = Column(Integer, default=0)
    barcode = Column(String)
    aisle = Column(String)
    row = Column(String)
    bin = Column(String)
    created_at = Column(
        DateTime, nullable=False, default=func.current_timestamp()
    )
    updated_at = Column(
        DateTime, nullable=False, default=func.current_timestamp()
    )

    user = relationship("User", back_populates="stocks")
    inventory = relationship("Inventory", back_populates="stocks")
    location = relationship("Location", back_populates="stocks")
    supplier = relationship("Supplier", back_populates="stocks")
    movements = relationship(Movement, back_populates="stock")
