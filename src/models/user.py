from datetime import datetime
from src.database.db_config import db


class User(db.Model):
    __tablename__ = "users"

    id            = db.Column(db.Integer, primary_key=True)
    full_name     = db.Column(db.String(100), nullable=False)
    email         = db.Column(db.String(100), unique=True, nullable=False)
    phone         = db.Column(db.String(15), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role          = db.Column(db.Enum("admin", "staff", "customer"), default="customer")
    avatar        = db.Column(db.String(255), nullable=True)
    is_active     = db.Column(db.Boolean, default=True)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at    = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    vehicles      = db.relationship("Vehicle", backref="owner", lazy=True,
                                    foreign_keys="Vehicle.user_id")
    bookings      = db.relationship("Booking", backref="customer", lazy=True,
                                    foreign_keys="Booking.customer_id")
    staff_profile = db.relationship("StaffProfile", backref="user",
                                    uselist=False, lazy=True)

    def to_dict(self):
        return {
            "id":         self.id,
            "full_name":  self.full_name,
            "email":      self.email,
            "phone":      self.phone,
            "role":       self.role,
            "is_active":  self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"


class StaffProfile(db.Model):
    __tablename__ = "staff_profiles"

    id        = db.Column(db.Integer, primary_key=True)
    user_id   = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    position  = db.Column(db.String(100), default="Nhân viên rửa xe")
    salary    = db.Column(db.Numeric(12, 2), default=0)
    hire_date = db.Column(db.Date, nullable=False)

    def to_dict(self):
        return {
            "id":        self.id,
            "user_id":   self.user_id,
            "position":  self.position,
            "salary":    float(self.salary),
            "hire_date": self.hire_date.isoformat() if self.hire_date else None,
        }