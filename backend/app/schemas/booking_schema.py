import uuid
from datetime import date, time, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel
from app.models.booking import ServiceType, BookingStatus
from app.models.customer import TierLevel


class BookingCreateRequest(BaseModel):
    vehicle_id: uuid.UUID
    booking_date: date
    time_slot: time
    service_type: ServiceType


class BookingResponse(BaseModel):
    booking_id: uuid.UUID
    customer_id: uuid.UUID
    vehicle_id: uuid.UUID
    booking_date: date
    time_slot: time
    service_type: ServiceType
    status: BookingStatus
    amount_charged: Optional[Decimal] = None
    points_earned: Optional[int] = None
    discount_applied: Optional[Decimal] = None
    tier_at_booking: TierLevel
    queue_priority: int
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class BookingCompleteRequest(BaseModel):
    amount_charged: Decimal


class AvailableSlotResponse(BaseModel):
    date: date
    time_slot: time
    capacity_remaining: int