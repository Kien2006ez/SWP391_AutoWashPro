import uuid
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field
from app.models.customer import TierLevel


class VehicleCreate(BaseModel):
    license_plate: str = Field(..., min_length=4, max_length=20)
    vehicle_type: Optional[str] = None
    brand: Optional[str] = None
    is_primary: bool = False


class VehicleResponse(BaseModel):
    vehicle_id: uuid.UUID
    license_plate: str
    vehicle_type: Optional[str]
    brand: Optional[str]
    is_primary: bool

    class Config:
        from_attributes = True


class CustomerRegisterRequest(BaseModel):
    phone_number: str = Field(..., min_length=9, max_length=15)
    otp_code: str = Field(..., min_length=6, max_length=6)
    full_name: str = Field(..., min_length=1, max_length=100)
    date_of_birth: Optional[date] = None


class CustomerUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None


class CustomerResponse(BaseModel):
    customer_id: uuid.UUID
    phone_number: str
    full_name: str
    email: Optional[str]
    tier_level: TierLevel
    total_points: int
    lifetime_points: int
    visit_count: int
    created_at: datetime
    vehicles: list[VehicleResponse] = []

    class Config:
        from_attributes = True


class CustomerTierProgressResponse(BaseModel):
    tier_level: TierLevel
    total_points: int
    points_to_next_tier: Optional[int]
    progress_percent: float