from sqlalchemy import Column, DateTime, Integer, String, Text, func
from sqlalchemy.orm import relationship

from app.models.db.images_category_association import ImagesCategoryAssociation

from .base import Base
from .inventory import Inventory


class Category(Base):
    """
    Database model for Category.

    Attributes:
        id (int): The primary key for the Category table.
        username (str): The unique username of the user.
        email (str): The unique email address of the user.
        password (str): The hashed password of the user.
    """

    __tablename__ = "dev_nuriko_categories"

    id = Column(Integer, primary_key=True, index=True)
    parent_id = Column(Integer, nullable=True)
    name = Column(String)
    description = Column(String)
    image = Column(Text, nullable=True)
    created_at = Column(
        DateTime, nullable=False, default=func.current_timestamp()
    )
    updated_at = Column(
        DateTime, nullable=False, default=func.current_timestamp()
    )

    inventories = relationship(Inventory, back_populates="category")
    image_associations = relationship(
        ImagesCategoryAssociation, back_populates="category"
    )
