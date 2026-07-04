"""
Research logging service — M7 (ML/Data Analyst)
Được gọi từ bookings.py (M3) và loyalty_engine.py (M4).
BR-32: chỉ INSERT, không UPDATE/DELETE.
"""
import hashlib
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.booking import Booking
from app.models.research_log import TransactionLog, TierChangeLog, BookingLog
from app.services.booking_service import calculate_lead_days


def _anonymize(customer_id: UUID) -> str:
    """Hash customer_id để ẩn danh trong research data."""
    return hashlib.sha256(str(customer_id).encode()).hexdigest()[:32]


def log_booking(db: Session, booking: Booking) -> None:
    """FR-28: ghi log khi tạo booking mới."""
    log = BookingLog(
        customer_ref=_anonymize(booking.customer_id),
        tier_at_booking=booking.tier_at_booking,
        booking_lead_days=calculate_lead_days(booking.booking_date),
        service_type=booking.service_type,
        promo_applied=booking.applied_promotion_id is not None,
    )
    db.add(log)
    db.commit()


def log_transaction(
    db: Session,
    booking: Booking,
    tier_changed: bool = False,
) -> None:
    """FR-26: ghi log sau khi hoàn thành rửa xe."""
    log = TransactionLog(
        customer_ref=_anonymize(booking.customer_id),
        tier_level=booking.tier_at_booking,
        service_type=booking.service_type,
        amount_vnd=booking.amount_charged or 0,
        points_earned=booking.points_earned or 0,
        points_redeemed=bool(booking.points_redeemed),
        booking_lead_days=calculate_lead_days(booking.booking_date),
        promo_used=booking.applied_promotion_id is not None,
        tier_changed=tier_changed,
    )
    db.add(log)
    db.commit()


def log_tier_change(
    db: Session,
    customer_id: UUID,
    old_tier,
    new_tier,
    reason: str,
) -> None:
    """FR-27: ghi log khi tier thay đổi."""
    log = TierChangeLog(
        customer_ref=_anonymize(customer_id),
        old_tier=old_tier,
        new_tier=new_tier,
        reason=reason,
    )
    db.add(log)
    db.commit()