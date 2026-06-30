"""
Pydantic Schemas dùng cho validate request/response của API.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, ConfigDict
from app.models import UserRole, UserStatus, BookingStatus

# ── User ──────────────────────────────────────────────────────────────────
class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: EmailStr
    phone: Optional[str] = None
    fullname: str
    role: UserRole
    status: UserStatus
    created_at: datetime

class UserUpdateRole(BaseModel):
    role: UserRole

class UserUpdateStatus(BaseModel):
    status: UserStatus

class PaginatedUsers(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[UserOut]

# ── Service ───────────────────────────────────────────────────────────────
class ServiceBase(BaseModel):
    name: str
    price: float
    duration_minutes: int
    description: Optional[str] = ""
    is_active: bool = True

class ServiceCreate(ServiceBase):
    pass

class ServiceUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    duration_minutes: Optional[int] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class ServiceOut(ServiceBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime

# ── Booking ───────────────────────────────────────────────────────────────
class BookingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    service_id: int
    vehicle_type: Optional[str] = None
    license_plate: Optional[str] = None
    booking_date: str
    booking_time: str
    status: BookingStatus
    total_price: float
    notes: Optional[str] = ""
    created_at: datetime

class BookingStatusUpdate(BaseModel):
    status: BookingStatus

class PaginatedBookings(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[BookingOut]

# ── Dashboard ─────────────────────────────────────────────────────────────
class RevenuePoint(BaseModel):
    date: str
    revenue: float
    bookings_count: int

class DashboardStats(BaseModel):
    total_users: int
    total_bookings: int
    total_revenue: float
    bookings_by_status: dict
    revenue_last_7_days: List[RevenuePoint]