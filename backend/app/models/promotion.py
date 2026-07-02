import uuid
import enum
from datetime import datetime

from sqlalchemy import (
    Column, String, Text, Numeric, Date, DateTime, Boolean, Integer,
    Enum as SAEnum, JSON,
)
from sqlalchemy.dialects.postgresql import UUID

from app.db.session import Base


class PromoType(str, enum.Enum):
    DISCOUNT = "Discount"
    BONUS_POINTS = "BonusPoints"
    FREE_WASH = "FreeWash"


class SystemPromotion(Base):
    __tablename__ = "system_promotions"

    promotion_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    promo_type = Column(SAEnum(PromoType), nullable=False)
    value = Column(Numeric(10, 2), nullable=False)

    target_tier = Column(JSON, nullable=False)

    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)

    is_active = Column(Boolean, nullable=False, default=True)
    usage_limit = Column(Integer, nullable=True)
    usage_count = Column(Integer, nullable=False, default=0)

    created_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    def is_eligible_for_tier(self, tier: str) -> bool:
        return tier in (self.target_tier or [])

    def __repr__(self):
        return f"<SystemPromotion {self.title} ({self.promo_type})>"