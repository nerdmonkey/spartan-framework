from sqlalchemy import Column, DateTime, Integer, String, Text, func
from sqlalchemy.orm import relationship

from app.models.images_supplier_association import ImagesSupplierAssociation

from .base import Base
from .stock import Stock


class Supplier(Base):
    """
    Database model for Supplier.

    Attributes:
        id (int): The primary key for the Supplier table.
        username (str): The unique username of the user.
        email (str): The unique email address of the user.
        password (str): The hashed password of the user.
    """

    __tablename__ = "dev_nuriko_suppliers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    address = Column(Text)
    postal_code = Column(Integer)
    zip_code = Column(Integer)
    region = Column(String)
    city = Column(String)
    country = Column(String)
    contact_title = Column(String)
    contact_name = Column(String)
    contact_phone = Column(String)
    contact_email = Column(String, unique=True, index=True)
    image = Column(Text, nullable=True)
    created_at = Column(
        DateTime, nullable=False, default=func.current_timestamp()
    )
    updated_at = Column(
        DateTime, nullable=False, default=func.current_timestamp()
    )

    stocks = relationship(Stock, back_populates="supplier")
    image_associations = relationship(
        ImagesSupplierAssociation, back_populates="supplier"
    )
