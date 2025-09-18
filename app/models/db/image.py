from sqlalchemy import Column, DateTime, Integer, String, func
from sqlalchemy.orm import relationship

from .base import Base


class Image(Base):
    """
    Database model for Image.

    Attributes:
        id (int): The primary key for the Image table.
        username (str): The unique username of the user.
        email (str): The unique email address of the user.
        password (str): The hashed password of the user.
    """

    __tablename__ = "dev_nuriko_images"

    id = Column(Integer, primary_key=True, index=True)
    item_type = Column(String)
    content_type = Column(String)
    object_key = Column(String)
    created_at = Column(
        DateTime, nullable=False, default=func.current_timestamp()
    )
    updated_at = Column(
        DateTime, nullable=False, default=func.current_timestamp()
    )

    inventory_associations = relationship(
        "ImagesInventoryAssociation", back_populates="image"
    )

    supplier_associations = relationship(
        "ImagesSupplierAssociation", back_populates="image"
    )

    category_associations = relationship(
        "ImagesCategoryAssociation", back_populates="image"
    )
