import uuid
import enum
from datetime import datetime

from sqlalchemy import Column, Integer, Date, DateTime, Text, ForeignKey, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


class PointTransactionType(str, enum.Enum):
    EARN = "Earn"
    REDEEM = "Redeem"
    EXPIRE = "Expire"
    BONUS = "Bonus"
    ADJUST = "Adjust"


class CustomerPoint(Base):
    __tablename__ = "customer_points"

    point_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.customer_id"), nullable=False, index=True)
    booking_id = Column(UUID(as_uuid=True), ForeignKey("bookings.booking_id"), nullable=True)

    transaction_type = Column(SAEnum(PointTransactionType), nullable=False)
    points_delta = Column(Integer, nullable=False)
    balance_after = Column(Integer, nullable=False)
    expiry_date = Column(Date, nullable=True)
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    customer = relationship("Customer", back_populates="points")
    booking = relationship("Booking", back_populates="points")

    def __repr__(self):
        return f"<CustomerPoint {self.transaction_type} {self.points_delta}>"