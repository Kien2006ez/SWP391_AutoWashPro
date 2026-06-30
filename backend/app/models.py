from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base

class UserRole(str, enum.Enum):
    CUSTOMER = 'customer'
    STAFF = 'staff'
    ADMIN = 'admin'

class UserStatus(str, enum.Enum):
    ACTIVE = 'active'
    LOCKED = 'locked'

class BookingStatus(str, enum.Enum):
    PENDING = 'pending'
    CONFIRMED = 'confirmed'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    fullname = Column(String)
    phone = Column(String)
    role = Column(Enum(UserRole), default=UserRole.CUSTOMER)
    status = Column(Enum(UserStatus), default=UserStatus.ACTIVE)
    created_at = Column(DateTime, default=datetime.utcnow)

class Service(Base):
    __tablename__ = "services"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    price = Column(Float)
    duration_minutes = Column(Integer)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    service_id = Column(Integer, ForeignKey("services.id"))
    status = Column(Enum(BookingStatus), default=BookingStatus.PENDING)
    total_price = Column(Float)
    booking_date = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)