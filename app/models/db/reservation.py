from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_serializer


class InventoryReservation(BaseModel):
    """
    Soft reservation model for cart items to prevent race conditions.
    Uses DynamoDB TTL for automatic cleanup.
    """

    reservation_id: str
    user_id: str
    variant_id: str
    cart_id: str
    quantity: int
    reserved_at: datetime
    expires_at: int  # Unix timestamp for DynamoDB TTL
    status: str = "ACTIVE"  # ACTIVE, EXPIRED, CONSUMED, CANCELLED

    model_config = ConfigDict()

    @field_serializer("reserved_at")
    def serialize_datetime(self, value: datetime) -> str:
        return value.isoformat()


class ReservationSummary(BaseModel):
    """Summary of reservations for a variant"""

    variant_id: str
    total_reserved: int
    active_reservations: int
    available_stock: int
    total_stock: int
