import uuid
from datetime import datetime

from sqlalchemy import Column, String, Integer, Numeric, Boolean, DateTime, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID

from app.db.session import Base
from app.models.customer import TierLevel
from app.models.booking import ServiceType


class TransactionLog(Base):
    __tablename__ = "transaction_log"

    log_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_ref = Column(String(64), nullable=False, index=True)

    tier_level = Column(SAEnum(TierLevel), nullable=False)
    service_type = Column(SAEnum(ServiceType), nullable=False)
    amount_vnd = Column(Numeric(12, 2), nullable=False)
    points_earned = Column(Integer, nullable=False)
    points_redeemed = Column(Boolean, nullable=False, default=False)
    booking_lead_days = Column(Integer, nullable=False)
    promo_used = Column(Boolean, nullable=False, default=False)
    tier_changed = Column(Boolean, nullable=False, default=False)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class TierChangeLog(Base):
    __tablename__ = "tier_change_log"

    log_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_ref = Column(String(64), nullable=False, index=True)
    old_tier = Column(SAEnum(TierLevel), nullable=False)
    new_tier = Column(SAEnum(TierLevel), nullable=False)
    reason = Column(String(30), nullable=False)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class BookingLog(Base):
    __tablename__ = "booking_log"

    log_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_ref = Column(String(64), nullable=False, index=True)
    tier_at_booking = Column(SAEnum(TierLevel), nullable=False)
    booking_lead_days = Column(Integer, nullable=False)
    service_type = Column(SAEnum(ServiceType), nullable=False)
    promo_applied = Column(Boolean, nullable=False, default=False)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)