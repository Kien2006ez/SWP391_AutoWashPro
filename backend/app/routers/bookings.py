from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.deps import get_current_customer
from app.models.customer import Customer
from app.models.customer import CustomerVehicle
from app.models.booking import Booking, BookingStatus
from app.schemas.booking_schema import (
    BookingCreateRequest, BookingResponse, AvailableSlotResponse,
)
from app.services import booking_service
from app.services.notification_service import send_sms

router = APIRouter()


@router.get("/available-slots", response_model=list[AvailableSlotResponse])
def get_available_slots(
    target_date: date,
    customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db),
):
    """Lấy danh sách slot còn chỗ — FR-05 bước 1."""
    if not booking_service.is_within_booking_window(customer, target_date):
        max_date = booking_service.get_max_booking_date(customer)
        raise HTTPException(
            status_code=400,
            detail=f"Ngày này nằm ngoài cửa sổ đặt lịch của bạn. Tối đa đến {max_date}.",
        )
    return booking_service.get_available_slots(db, target_date)


@router.post("", response_model=BookingResponse, status_code=201)
def create_booking(
    payload: BookingCreateRequest,
    customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db),
):
    """FR-05: Đặt lịch rửa xe."""
    # Kiểm tra xe thuộc về customer này
    vehicle = (
        db.query(CustomerVehicle)
        .filter(
            CustomerVehicle.vehicle_id == payload.vehicle_id,
            CustomerVehicle.customer_id == customer.customer_id,
        )
        .first()
    )
    if not vehicle:
        raise HTTPException(status_code=404, detail="Xe không tồn tại trong tài khoản của bạn.")

    try:
        booking = booking_service.create_booking(
            db=db,
            customer=customer,
            vehicle_id=payload.vehicle_id,
            booking_date=payload.booking_date,
            time_slot=payload.time_slot,
            service_type=payload.service_type,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # FR-28: ghi log booking cho research
    from app.services import research_service
    research_service.log_booking(db, booking)

    # FR-07: gửi thông báo xác nhận
    send_sms(
        customer.phone_number,
        f"Da dat lich: {booking.booking_date} luc {booking.time_slot}. "
        f"Dich vu: {booking.service_type.value}.",
    )
    return booking


@router.get("/upcoming", response_model=list[BookingResponse])
def get_upcoming_bookings(
    customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db),
):
    """FR-16: xem lịch đặt sắp tới."""
    return (
        db.query(Booking)
        .filter(
            Booking.customer_id == customer.customer_id,
            Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED]),
        )
        .order_by(Booking.booking_date.asc(), Booking.time_slot.asc())
        .all()
    )


@router.get("/history", response_model=list[BookingResponse])
def get_wash_history(
    customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db),
):
    """FR-15: xem lịch sử rửa xe (đã hoàn thành)."""
    return (
        db.query(Booking)
        .filter(
            Booking.customer_id == customer.customer_id,
            Booking.status == BookingStatus.COMPLETED,
        )
        .order_by(Booking.completed_at.desc())
        .all()
    )


@router.patch("/{booking_id}/cancel", response_model=BookingResponse)
def cancel_booking(
    booking_id: UUID,
    customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db),
):
    """FR-06: hủy lịch — BR-12 chỉ được hủy trước 2 tiếng."""
    booking = (
        db.query(Booking)
        .filter(
            Booking.booking_id == booking_id,
            Booking.customer_id == customer.customer_id,
        )
        .first()
    )
    if not booking:
        raise HTTPException(status_code=404, detail="Không tìm thấy lịch đặt.")

    if booking.status not in (BookingStatus.PENDING, BookingStatus.CONFIRMED):
        raise HTTPException(status_code=400, detail="Lịch này không thể hủy.")

    if not booking_service.can_cancel(booking):
        raise HTTPException(
            status_code=400,
            detail="Chỉ được hủy lịch trước ít nhất 2 tiếng.",
        )

    booking.status = BookingStatus.CANCELLED
    db.commit()
    db.refresh(booking)
    return booking