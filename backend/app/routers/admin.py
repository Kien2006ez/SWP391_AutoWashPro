"""
Admin Core Router — M3 (Backend Developer)
FR-18: Xem danh sách booking
FR-19: Đánh dấu hoàn thành + tính điểm
FR-20: Analytics (doanh thu, tier distribution)
FR-21: Cấu hình tier rules
FR-22: Quản lý customer + chỉnh điểm thủ công
"""
from datetime import date, datetime
from uuid import UUID
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.session import get_db
from app.core.deps import get_current_admin
from app.models.admin_user import AdminUser
from app.models.booking import Booking, BookingStatus
from app.models.customer import Customer, TierLevel
from app.models.loyalty import CustomerPoint, PointTransactionType
from app.schemas.booking_schema import BookingResponse, BookingCompleteRequest
from app.services import loyalty_engine, research_service

router = APIRouter()


# ── FR-18: Xem danh sách booking ────────────────────────────
@router.get("/bookings", response_model=list[BookingResponse])
def list_bookings(
    booking_date: date = None,
    status: BookingStatus = None,
    admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """FR-18: Admin xem toàn bộ booking, có thể lọc theo ngày và status."""
    query = db.query(Booking)
    if booking_date:
        query = query.filter(Booking.booking_date == booking_date)
    if status:
        query = query.filter(Booking.status == status)
    return query.order_by(
        Booking.booking_date.desc(),
        Booking.queue_priority.desc()
    ).all()


# ── FR-19: Đánh dấu hoàn thành + tính điểm ─────────────────
@router.patch("/bookings/{booking_id}/complete", response_model=BookingResponse)
def complete_booking(
    booking_id: UUID,
    payload: BookingCompleteRequest,
    admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """
    FR-19: Admin đánh dấu rửa xong → tự động tính điểm (FR-08)
    và ghi research log (FR-26).
    """
    booking = db.query(Booking).filter(
        Booking.booking_id == booking_id
    ).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking không tồn tại.")
    if booking.status == BookingStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Booking này đã hoàn thành rồi.")
    if booking.status == BookingStatus.CANCELLED:
        raise HTTPException(status_code=400, detail="Booking đã bị hủy, không thể hoàn thành.")

    # Cập nhật booking
    booking.status = BookingStatus.COMPLETED
    booking.amount_charged = payload.amount_charged
    booking.completed_at = datetime.utcnow()
    db.commit()
    db.refresh(booking)

    # Lấy customer để tính điểm
    customer = db.query(Customer).filter(
        Customer.customer_id == booking.customer_id
    ).first()

    # FR-08: tính và cộng điểm
    old_tier = customer.tier_level
    loyalty_engine.award_points(db=db, customer=customer, booking=booking)

    # FR-26: ghi research log
    tier_changed = customer.tier_level != old_tier
    research_service.log_transaction(db, booking, tier_changed=tier_changed)

    db.refresh(booking)
    return booking


# ── FR-20: Revenue Analytics ─────────────────────────────────
@router.get("/analytics")
def get_analytics(
    from_date: date = Query(default=None),
    to_date: date = Query(default=None),
    admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """FR-20: Doanh thu, tier distribution, repeat rate."""
    query = db.query(Booking).filter(
        Booking.status == BookingStatus.COMPLETED
    )
    if from_date:
        query = query.filter(Booking.booking_date >= from_date)
    if to_date:
        query = query.filter(Booking.booking_date <= to_date)

    completed = query.all()

    total_revenue = sum(
        float(b.amount_charged or 0) for b in completed
    )
    total_bookings = len(completed)
    avg_order_value = total_revenue / total_bookings if total_bookings > 0 else 0

    # Tier distribution
    tier_counts = dict(
        db.query(Customer.tier_level, func.count(Customer.customer_id))
        .group_by(Customer.tier_level)
        .all()
    )

    # Doanh thu theo service type
    revenue_by_service = {}
    for b in completed:
        key = b.service_type.value
        revenue_by_service[key] = revenue_by_service.get(key, 0) + float(b.amount_charged or 0)

    return {
        "total_revenue_vnd": total_revenue,
        "total_completed_bookings": total_bookings,
        "average_order_value_vnd": round(avg_order_value, 2),
        "tier_distribution": {
            tier.value: tier_counts.get(tier, 0)
            for tier in TierLevel
        },
        "revenue_by_service_type": revenue_by_service,
    }


# ── FR-21: Cấu hình tier rules ───────────────────────────────
@router.get("/config/tiers")
def get_tier_config(admin: AdminUser = Depends(get_current_admin)):
    """FR-21: Xem cấu hình tier hiện tại."""
    from app.models.customer import (
        TIER_BOOKING_WINDOW_DAYS,
        TIER_POINT_MULTIPLIER,
        TIER_MIN_POINTS_3M,
        TIER_BIRTHDAY_BONUS,
        TIER_FREE_WASH_PER_MONTH,
    )
    return {
        tier.value: {
            "booking_window_days": TIER_BOOKING_WINDOW_DAYS[tier],
            "point_multiplier": TIER_POINT_MULTIPLIER[tier],
            "min_points_3_months": TIER_MIN_POINTS_3M[tier],
            "birthday_bonus_points": TIER_BIRTHDAY_BONUS[tier],
            "free_wash_per_month": TIER_FREE_WASH_PER_MONTH[tier],
        }
        for tier in TierLevel
    }


# ── FR-22: Quản lý customer ───────────────────────────────────
@router.get("/customers")
def list_customers(
    search: str = Query(default=None),
    admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """FR-22: Danh sách customer, tìm kiếm theo tên hoặc số điện thoại."""
    query = db.query(Customer)
    if search:
        query = query.filter(
            Customer.phone_number.contains(search) |
            Customer.full_name.ilike(f"%{search}%")
        )
    customers = query.order_by(Customer.created_at.desc()).all()
    return [
        {
            "customer_id": str(c.customer_id),
            "full_name": c.full_name,
            "phone_number": c.phone_number,
            "tier_level": c.tier_level.value,
            "total_points": c.total_points,
            "lifetime_points": c.lifetime_points,
            "visit_count": c.visit_count,
        }
        for c in customers
    ]


@router.patch("/customers/{customer_id}/points")
def adjust_customer_points(
    customer_id: UUID,
    points_delta: int,
    reason: str,
    admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """
    FR-22: Chỉnh điểm thủ công.
    BR-27: Bắt buộc phải có lý do, ghi audit log.
    """
    if not reason or not reason.strip():
        raise HTTPException(
            status_code=400,
            detail="Phải nhập lý do điều chỉnh điểm (BR-27)."
        )

    customer = db.query(Customer).filter(
        Customer.customer_id == customer_id
    ).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer không tồn tại.")

    new_balance = max(0, customer.total_points + points_delta)

    point_record = CustomerPoint(
        customer_id=customer.customer_id,
        transaction_type=PointTransactionType.ADJUST,
        points_delta=points_delta,
        balance_after=new_balance,
        notes=f"[Admin: {admin.username}] {reason}",
    )
    db.add(point_record)
    customer.total_points = new_balance
    db.commit()

    return {
        "message": "Điều chỉnh điểm thành công.",
        "customer_id": str(customer_id),
        "points_adjusted": points_delta,
        "new_balance": new_balance,
    }