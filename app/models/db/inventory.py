from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from app.models.db.images_inventory_association import (
    ImagesInventoryAssociation,
)

from .base import Base
from .stock import Stock


class Inventory(Base):
    """
    Database model for Inventory.

    Attributes:
        id (int): The primary key for the Inventory table.
        username (str): The unique username of the user.
        email (str): The unique email address of the user.
        password (str): The hashed password of the user.
    """

    __tablename__ = "dev_nuriko_inventories"

    id = Column(Integer, primary_key=True, index=True)
    parent_id = Column(Integer, nullable=True)
    category_id = Column(Integer, ForeignKey("dev_nuriko_categories.id"))
    name = Column(String)
    description = Column(String)
    image = Column(Text, nullable=True)
    created_at = Column(
        DateTime, nullable=False, default=func.current_timestamp()
    )
    updated_at = Column(
        DateTime, nullable=False, default=func.current_timestamp()
    )

    category = relationship("Category", back_populates="inventories")
    stocks = relationship(Stock, back_populates="inventory")

    image_associations = relationship(
        ImagesInventoryAssociation, back_populates="inventory"
    )
