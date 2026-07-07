from datetime import date, datetime, time, timedelta
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.customer import Customer, TIER_BOOKING_WINDOW_DAYS, TierLevel
from app.models.booking import Booking, BookingStatus, ServiceType

# Khung giờ mỗi ngày: 8h - 17h
DAILY_TIME_SLOTS = [time(h, 0) for h in range(8, 18)]

# Số xe tối đa mỗi slot (BR-09)
SLOT_CAPACITY = 3

# Độ ưu tiên theo tier (BR-10) — số càng cao càng được ưu tiên
TIER_QUEUE_PRIORITY = {
    TierLevel.MEMBER: 0,
    TierLevel.SILVER: 1,
    TierLevel.GOLD: 2,
    TierLevel.PLATINUM: 3,
}

# Deadline hủy lịch: phải hủy trước ít nhất 2 tiếng (BR-12)
CANCEL_DEADLINE_HOURS = 2


def get_max_booking_date(customer: Customer) -> date:
    """BR-08: ngày tối đa được đặt tùy theo tier."""
    days = TIER_BOOKING_WINDOW_DAYS[customer.tier_level]
    return date.today() + timedelta(days=days)


def is_within_booking_window(customer: Customer, booking_date: date) -> bool:
    return date.today() <= booking_date <= get_max_booking_date(customer)


def get_available_slots(db: Session, target_date: date) -> list[dict]:
    """Trả về danh sách slot còn chỗ trong ngày target_date."""
    booked_counts = dict(
        db.query(Booking.time_slot, func.count(Booking.booking_id))
        .filter(
            Booking.booking_date == target_date,
            Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED]),
        )
        .group_by(Booking.time_slot)
        .all()
    )
    return [
        {
            "date": target_date,
            "time_slot": slot,
            "capacity_remaining": SLOT_CAPACITY - booked_counts.get(slot, 0),
        }
        for slot in DAILY_TIME_SLOTS
    ]


def is_slot_available(db: Session, booking_date: date, time_slot: time) -> bool:
    """BR-09: kiểm tra slot còn chỗ không."""
    count = (
        db.query(func.count(Booking.booking_id))
        .filter(
            Booking.booking_date == booking_date,
            Booking.time_slot == time_slot,
            Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED]),
        )
        .scalar()
    )
    return count < SLOT_CAPACITY


def can_cancel(booking: Booking) -> bool:
    """BR-12: chỉ hủy được nếu còn hơn 2 tiếng trước giờ rửa."""
    scheduled = datetime.combine(booking.booking_date, booking.time_slot)
    return scheduled - datetime.utcnow() > timedelta(hours=CANCEL_DEADLINE_HOURS)


def calculate_lead_days(booking_date: date) -> int:
    return (booking_date - date.today()).days


def create_booking(
    db: Session,
    customer: Customer,
    vehicle_id: UUID,
    booking_date: date,
    time_slot: time,
    service_type: ServiceType,
) -> Booking:
    """FR-05: tạo booking, kiểm tra BR-08 và BR-09."""
    if not is_within_booking_window(customer, booking_date):
        max_date = get_max_booking_date(customer)
        raise ValueError(
            f"Ngày đặt vượt quá giới hạn của tier {customer.tier_level.value}. "
            f"Bạn chỉ được đặt đến ngày {max_date}."
        )

    # Trước đây thiếu bước này: chỉ kiểm tra "còn chỗ trống" mà không
    # kiểm tra giờ gửi lên có nằm trong khung giờ hoạt động hay không,
    # nên có thể tạo booking vào giờ bất kỳ (vd 03:00, 23:00...).
    if time_slot not in DAILY_TIME_SLOTS:
        raise ValueError(
            "Giờ đặt không hợp lệ. Chỉ nhận đặt lịch trong khung giờ hoạt động "
            f"({DAILY_TIME_SLOTS[0].strftime('%H:%M')} - {DAILY_TIME_SLOTS[-1].strftime('%H:%M')})."
        )

    if not is_slot_available(db, booking_date, time_slot):
        raise ValueError("Slot này đã đầy. Vui lòng chọn giờ khác.")

    booking = Booking(
        customer_id=customer.customer_id,
        vehicle_id=vehicle_id,
        booking_date=booking_date,
        time_slot=time_slot,
        service_type=service_type,
        status=BookingStatus.PENDING,
        tier_at_booking=customer.tier_level,
        queue_priority=TIER_QUEUE_PRIORITY[customer.tier_level],
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking