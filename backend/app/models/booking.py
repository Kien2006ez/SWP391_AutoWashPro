import uuid
import enum
from datetime import datetime

from sqlalchemy import (
    Column, Integer, Numeric, Date, Time, DateTime,
    ForeignKey, Enum as SAEnum,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base
from app.models.customer import TierLevel


class ServiceType(str, enum.Enum):
    BASIC = "Basic"
    PREMIUM = "Premium"
    DELUXE = "Deluxe"


class BookingStatus(str, enum.Enum):
    PENDING = "Pending"
    CONFIRMED = "Confirmed"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"


class Booking(Base):
    __tablename__ = "bookings"

    booking_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.customer_id"), nullable=False, index=True)
    vehicle_id = Column(UUID(as_uuid=True), ForeignKey("customer_vehicles.vehicle_id"), nullable=False)
    applied_promotion_id = Column(UUID(as_uuid=True), ForeignKey("system_promotions.promotion_id"), nullable=True)

    booking_date = Column(Date, nullable=False, index=True)
    time_slot = Column(Time, nullable=False)
    service_type = Column(SAEnum(ServiceType), nullable=False)
    status = Column(SAEnum(BookingStatus), nullable=False, default=BookingStatus.PENDING)

    amount_charged = Column(Numeric(12, 2), nullable=True)
    points_earned = Column(Integer, nullable=True)
    points_redeemed = Column(Integer, nullable=True)
    discount_applied = Column(Numeric(12, 2), nullable=True)

    tier_at_booking = Column(SAEnum(TierLevel), nullable=False)
    queue_priority = Column(Integer, nullable=False, default=0)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    customer = relationship("Customer", back_populates="bookings")
    vehicle = relationship("CustomerVehicle", back_populates="bookings")
    points = relationship("CustomerPoint", back_populates="booking")

    def __repr__(self):
        return f"<Booking {self.booking_id} {self.status} {self.booking_date}>"