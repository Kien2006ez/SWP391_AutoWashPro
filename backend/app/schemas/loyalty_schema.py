import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, field_validator
from app.models.loyalty import PointTransactionType
from app.models.promotion import PromoType


class PointTransactionResponse(BaseModel):
    point_id: uuid.UUID
    transaction_type: PointTransactionType
    points_delta: int
    balance_after: int
    expiry_date: Optional[date] = None
    created_at: datetime

    class Config:
        from_attributes = True


class RedeemPointsRequest(BaseModel):
    points_cost: int
    reward_description: str


class PromotionCreateRequest(BaseModel):
    title: str
    promo_type: PromoType
    value: Decimal
    target_tier: list[str]
    start_date: date
    end_date: date
    usage_limit: Optional[int] = None

    @field_validator("end_date")
    @classmethod
    def end_after_start(cls, v, info):
        if info.data.get("start_date") and v < info.data["start_date"]:
            raise ValueError("end_date phải sau start_date.")
        return v


class PromotionResponse(BaseModel):
    promotion_id: uuid.UUID
    title: str
    promo_type: PromoType
    value: Decimal
    target_tier: list[str]
    start_date: date
    end_date: date
    is_active: bool
    usage_count: int

    class Config:
        from_attributes = True