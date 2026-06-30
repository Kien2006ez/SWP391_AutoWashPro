"""
Router: /api/admin
--------------------
Các API dành riêng cho Admin, yêu cầu xác thực JWT + role=admin
(thông qua dependency `require_admin`).
"""

from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.dependencies import require_admin
from app.models import User, Service, Booking, UserStatus, BookingStatus
from app.schemas import (
    UserOut, UserUpdateRole, UserUpdateStatus, PaginatedUsers,
    ServiceCreate, ServiceUpdate, ServiceOut,
    BookingOut, BookingStatusUpdate, PaginatedBookings,
    DashboardStats, RevenuePoint,
)

router = APIRouter(
    prefix="/api/admin",
    tags=["Admin"],
    dependencies=[Depends(require_admin)],  # Áp dụng cho TOÀN BỘ route bên dưới
)

# 1. QUẢN LÝ USERS

@router.get("/users", response_model=PaginatedUsers)
def list_users(
    db: Session = Depends(get_db),
    keyword: Optional[str] = Query(None, description="Tìm theo tên/email/sđt"),
    role: Optional[str] = Query(None, description="Lọc theo role"),
    status_filter: Optional[str] = Query(None, alias="status", description="Lọc theo status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """Danh sách user, hỗ trợ tìm kiếm + lọc + phân trang."""
    query = db.query(User)

    if keyword:
        like = f"%{keyword}%"
        query = query.filter(
            (User.fullname.ilike(like)) |
            (User.email.ilike(like)) |
            (User.phone.ilike(like))
        )
    if role:
        query = query.filter(User.role == role)
    if status_filter:
        query = query.filter(User.status == status_filter)

    total = query.count()
    items = (
        query.order_by(User.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return PaginatedUsers(total=total, page=page, page_size=page_size, items=items)

@router.get("/users/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Không tìm thấy người dùng")
    return user

@router.patch("/users/{user_id}/status", response_model=UserOut)
def update_user_status(
    user_id: int,
    payload: UserUpdateStatus,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin),
):
    """Khóa hoặc mở khóa tài khoản người dùng."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Không tìm thấy người dùng")

    if user.id == current_admin.id and payload.status == UserStatus.LOCKED:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Không thể tự khóa tài khoản của chính mình")

    user.status = payload.status
    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    return user

@router.patch("/users/{user_id}/role", response_model=UserOut)
def update_user_role(
    user_id: int,
    payload: UserUpdateRole,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin),
):
    """Thay đổi vai trò người dùng (customer / staff / admin)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Không tìm thấy người dùng")

    if user.id == current_admin.id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Không thể tự đổi role của chính mình")

    user.role = payload.role
    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    return user


# 2. QUẢN LÝ BOOKINGS

@router.get("/bookings", response_model=PaginatedBookings)
def list_bookings(
    db: Session = Depends(get_db),
    status_filter: Optional[str] = Query(None, alias="status"),
    date_from: Optional[str] = Query(None, description="YYYY-MM-DD"),
    date_to: Optional[str] = Query(None, description="YYYY-MM-DD"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """Xem toàn bộ booking trong hệ thống, lọc theo trạng thái/khoảng ngày."""
    query = db.query(Booking)

    if status_filter:
        query = query.filter(Booking.status == status_filter)
    if date_from:
        query = query.filter(Booking.booking_date >= date_from)
    if date_to:
        query = query.filter(Booking.booking_date <= date_to)

    total = query.count()
    items = (
        query.order_by(Booking.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return PaginatedBookings(total=total, page=page, page_size=page_size, items=items)

@router.get("/bookings/{booking_id}", response_model=BookingOut)
def get_booking(booking_id: int, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Không tìm thấy booking")
    return booking

@router.patch("/bookings/{booking_id}/confirm", response_model=BookingOut)
def confirm_booking(booking_id: int, db: Session = Depends(get_db)):
    """Duyệt một booking đang ở trạng thái pending."""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Không tìm thấy booking")
    if booking.status != BookingStatus.PENDING:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"Chỉ có thể duyệt booking ở trạng thái 'pending' (hiện tại: '{booking.status.value}')",
        )

    booking.status = BookingStatus.CONFIRMED
    booking.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(booking)
    return booking

@router.patch("/bookings/{booking_id}/cancel", response_model=BookingOut)
def cancel_booking(booking_id: int, db: Session = Depends(get_db)):
    """Admin hủy một booking (chỉ khi chưa hoàn thành)."""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Không tìm thấy booking")
    if booking.status in (BookingStatus.COMPLETED, BookingStatus.CANCELLED):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"Không thể hủy booking đã ở trạng thái '{booking.status.value}'",
        )

    booking.status = BookingStatus.CANCELLED
    booking.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(booking)
    return booking


# 3. DASHBOARD THỐNG KÊ DOANH THU

@router.get("/dashboard", response_model=DashboardStats)
def get_dashboard_stats(db: Session = Depends(get_db)):
    """Tổng quan: tổng user, tổng booking, tổng doanh thu, doanh thu 7 ngày gần nhất."""
    total_users = db.query(func.count(User.id)).scalar() or 0
    total_bookings = db.query(func.count(Booking.id)).scalar() or 0

    total_revenue = (
        db.query(func.coalesce(func.sum(Booking.total_price), 0))
        .filter(Booking.status == BookingStatus.COMPLETED)
        .scalar()
        or 0
    )

    status_counts = (
        db.query(Booking.status, func.count(Booking.id))
        .group_by(Booking.status)
        .all()
    )
    bookings_by_status = {s.value: c for s, c in status_counts}
    for s in BookingStatus:
        bookings_by_status.setdefault(s.value, 0)

    today = datetime.utcnow().date()
    seven_days_ago = (today - timedelta(days=6)).isoformat()

    revenue_rows = (
        db.query(
            Booking.booking_date,
            func.coalesce(func.sum(Booking.total_price), 0),
            func.count(Booking.id),
        )
        .filter(Booking.status == BookingStatus.COMPLETED)
        .filter(Booking.booking_date >= seven_days_ago)
        .group_by(Booking.booking_date)
        .order_by(Booking.booking_date)
        .all()
    )

    revenue_map = {date: (rev, cnt) for date, rev, cnt in revenue_rows}
    revenue_last_7_days = []
    for i in range(7):
        d = (today - timedelta(days=6 - i)).isoformat()
        rev, cnt = revenue_map.get(d, (0, 0))
        revenue_last_7_days.append(RevenuePoint(date=d, revenue=rev, bookings_count=cnt))

    return DashboardStats(
        total_users=total_users,
        total_bookings=total_bookings,
        total_revenue=total_revenue,
        bookings_by_status=bookings_by_status,
        revenue_last_7_days=revenue_last_7_days,
    )


# ============================================================================
# 4. QUẢN LÝ SERVICES (CRUD)
# ============================================================================

@router.get("/services", response_model=list[ServiceOut])
def list_services(db: Session = Depends(get_db)):
    """Lấy toàn bộ dịch vụ (kể cả đã ẩn) - dành cho trang quản trị."""
    return db.query(Service).order_by(Service.id).all()

@router.post("/services", response_model=ServiceOut, status_code=status.HTTP_201_CREATED)
def create_service(payload: ServiceCreate, db: Session = Depends(get_db)):
    """Tạo dịch vụ mới."""
    service = Service(**payload.model_dump())
    db.add(service)
    db.commit()
    db.refresh(service)
    return service

@router.put("/services/{service_id}", response_model=ServiceOut)
def update_service(service_id: int, payload: ServiceUpdate, db: Session = Depends(get_db)):
    """Cập nhật thông tin dịch vụ."""
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Không tìm thấy dịch vụ")

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(service, key, value)
    service.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(service)
    return service

@router.delete("/services/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_service(service_id: int, db: Session = Depends(get_db)):
    """Xóa dịch vụ. Nếu đã có booking liên kết, soft-delete (is_active=False) thay vì xóa cứng."""
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Không tìm thấy dịch vụ")

    has_bookings = db.query(Booking).filter(Booking.service_id == service_id).first()
    if has_bookings:
        service.is_active = False
        db.commit()
        return

    db.delete(service)
    db.commit()