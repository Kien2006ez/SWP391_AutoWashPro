import uuid
import enum
from datetime import datetime, date

from sqlalchemy import (
    Column, String, Integer, Numeric, Date, DateTime,
    Boolean, ForeignKey, Enum as SAEnum,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


class TierLevel(str, enum.Enum):
    MEMBER = "Member"
    SILVER = "Silver"
    GOLD = "Gold"
    PLATINUM = "Platinum"


TIER_BOOKING_WINDOW_DAYS = {
    TierLevel.MEMBER: 7,
    TierLevel.SILVER: 10,
    TierLevel.GOLD: 12,
    TierLevel.PLATINUM: 14,
}

TIER_POINT_MULTIPLIER = {
    TierLevel.MEMBER: 1.0,
    TierLevel.SILVER: 1.2,
    TierLevel.GOLD: 1.5,
    TierLevel.PLATINUM: 2.0,
}

TIER_MIN_POINTS_3M = {
    TierLevel.MEMBER: 0,
    TierLevel.SILVER: 500,
    TierLevel.GOLD: 1500,
    TierLevel.PLATINUM: 3000,
}

TIER_BIRTHDAY_BONUS = {
    TierLevel.MEMBER: 0,
    TierLevel.SILVER: 100,
    TierLevel.GOLD: 200,
    TierLevel.PLATINUM: 500,
}

TIER_FREE_WASH_PER_MONTH = {
    TierLevel.MEMBER: 0,
    TierLevel.SILVER: 0,
    TierLevel.GOLD: 1,
    TierLevel.PLATINUM: 2,
}


class Customer(Base):
    __tablename__ = "customers"

    customer_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    phone_number = Column(String(15), unique=True, nullable=False, index=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(150), nullable=True)
    date_of_birth = Column(Date, nullable=True)

    tier_level = Column(SAEnum(TierLevel), nullable=False, default=TierLevel.MEMBER)

    total_points = Column(Integer, nullable=False, default=0)
    lifetime_points = Column(Integer, nullable=False, default=0)
    total_spent_3m = Column(Numeric(12, 2), nullable=False, default=0)
    visit_count = Column(Integer, nullable=False, default=0)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    vehicles = relationship("CustomerVehicle", back_populates="customer", cascade="all, delete-orphan")
    bookings = relationship("Booking", back_populates="customer")
    points = relationship("CustomerPoint", back_populates="customer")

    def __repr__(self):
        return f"<Customer {self.phone_number} tier={self.tier_level}>"


class CustomerVehicle(Base):
    __tablename__ = "customer_vehicles"

    vehicle_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.customer_id"), nullable=False, index=True)

    license_plate = Column(String(20), unique=True, nullable=False)
    vehicle_type = Column(String(50), nullable=True)
    brand = Column(String(50), nullable=True)
    is_primary = Column(Boolean, nullable=False, default=False)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    customer = relationship("Customer", back_populates="vehicles")
    bookings = relationship("Booking", back_populates="vehicle")

    def __repr__(self):
        return f"<CustomerVehicle {self.license_plate}>"