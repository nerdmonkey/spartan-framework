from sqlalchemy import Column, DateTime, ForeignKey, Integer, func
from sqlalchemy.orm import relationship

from .base import Base


class ImagesCategoryAssociation(Base):
    """
    Database model for Images_category_association.

    Attributes:
        id (int): The primary key for the Images_category_association table.
        username (str): The unique username of the user.
        email (str): The unique email address of the user.
        password (str): The hashed password of the user.
    """

    __tablename__ = "dev_nuriko_images_categories_association"

    image_id = Column(
        Integer, ForeignKey("dev_nuriko_images.id"), primary_key=True
    )
    category_id = Column(
        Integer, ForeignKey("dev_nuriko_categories.id"), primary_key=True
    )
    created_at = Column(
        DateTime, nullable=False, default=func.current_timestamp()
    )
    updated_at = Column(
        DateTime, nullable=False, default=func.current_timestamp()
    )

    image = relationship("Image", back_populates="category_associations")
    category = relationship("Category", back_populates="image_associations")
