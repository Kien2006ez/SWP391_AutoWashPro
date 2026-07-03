"""
Loyalty Engine — M4 (Frontend Developer kiêm Loyalty Logic)

Các function trong file này được gọi từ:
- admin.py (M3) gọi award_points() sau khi complete booking
- jobs/ (M4) gọi run_monthly_tier_review() mỗi tháng
- bookings.py (M3) gọi apply_tier_perks() lúc tạo booking
"""
from datetime import date, datetime, timedelta
from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.customer import (
    Customer, TierLevel,
    TIER_POINT_MULTIPLIER, TIER_MIN_POINTS_3M,
    TIER_FREE_WASH_PER_MONTH, TIER_BIRTHDAY_BONUS,
)
from app.models.booking import Booking, BookingStatus
from app.models.loyalty import CustomerPoint, PointTransactionType
from app.services.notification_service import send_sms


def award_points(
    db: Session,
    customer: Customer,
    booking: Booking,
) -> int:
    """
    FR-08: Tính và cộng điểm sau khi rửa xe xong.
    BR-13: points = floor(amount / 1000) * tier_multiplier
    BR-14: điểm hết hạn sau 12 tháng
    """
    amount = booking.amount_charged or Decimal("0")
    multiplier = TIER_POINT_MULTIPLIER[customer.tier_level]
    points_earned = int(amount / 1000) * multiplier
    points_earned = int(points_earned)

    if points_earned <= 0:
        return 0

    new_balance = customer.total_points + points_earned

    # Ghi vào bảng customer_points
    point_record = CustomerPoint(
        customer_id=customer.customer_id,
        booking_id=booking.booking_id,
        transaction_type=PointTransactionType.EARN,
        points_delta=points_earned,
        balance_after=new_balance,
        expiry_date=date.today() + timedelta(days=365),  # BR-14
    )
    db.add(point_record)

    # Cập nhật tổng điểm customer
    customer.total_points = new_balance
    customer.lifetime_points += points_earned
    customer.visit_count += 1
    customer.total_spent_3m = (customer.total_spent_3m or 0) + amount

    # Cập nhật booking
    booking.points_earned = points_earned

    db.commit()

    send_sms(
        customer.phone_number,
        f"Ban da duoc cong {points_earned} diem. "
        f"So du hien tai: {new_balance} diem.",
    )
    return points_earned


def redeem_points(
    db: Session,
    customer: Customer,
    points_cost: int,
    reward_description: str,
) -> bool:
    """
    FR-11: Đổi điểm lấy phần thưởng.
    BR-19: phải đủ điểm mới đổi được
    BR-20: tối thiểu 200 điểm
    """
    if points_cost < 200:
        raise ValueError("Cần tối thiểu 200 điểm để đổi thưởng.")
    if customer.total_points < points_cost:
        raise ValueError(
            f"Không đủ điểm. Hiện có {customer.total_points}, cần {points_cost}."
        )

    new_balance = customer.total_points - points_cost

    point_record = CustomerPoint(
        customer_id=customer.customer_id,
        transaction_type=PointTransactionType.REDEEM,
        points_delta=-points_cost,
        balance_after=new_balance,
        notes=reward_description,
    )
    db.add(point_record)

    customer.total_points = new_balance
    db.commit()
    return True


def run_monthly_tier_review(db: Session) -> dict:
    """
    FR-09: Review tier hàng tháng.
    BR-15: upgrade áp dụng ngay.
    BR-16: downgrade áp dụng tháng sau.
    BR-17: tính điểm 3 tháng gần nhất.
    Được gọi bởi cron job ngày 1 hàng tháng.
    """
    three_months_ago = date.today() - timedelta(days=90)

    # Tính điểm mỗi customer trong 3 tháng gần nhất
    point_sums = dict(
        db.query(
            CustomerPoint.customer_id,
            func.sum(CustomerPoint.points_delta),
        )
        .filter(
            CustomerPoint.created_at >= three_months_ago,
            CustomerPoint.transaction_type.in_([
                PointTransactionType.EARN,
                PointTransactionType.BONUS,
            ]),
        )
        .group_by(CustomerPoint.customer_id)
        .all()
    )

    upgraded, downgraded = 0, 0
    tier_order = [TierLevel.MEMBER, TierLevel.SILVER, TierLevel.GOLD, TierLevel.PLATINUM]

    customers = db.query(Customer).all()
    for customer in customers:
        points_3m = point_sums.get(customer.customer_id, 0)
        current_index = tier_order.index(customer.tier_level)

        # Tìm tier phù hợp nhất
        new_tier = TierLevel.MEMBER
        for tier in reversed(tier_order):
            if points_3m >= TIER_MIN_POINTS_3M[tier]:
                new_tier = tier
                break

        new_index = tier_order.index(new_tier)

        if new_index > current_index:
            # BR-15: Upgrade ngay
            old_tier = customer.tier_level
            customer.tier_level = new_tier
            db.commit()
            upgraded += 1

            # Ghi tier_change_log cho research (M7)
            from app.services import research_service
            research_service.log_tier_change(
                db, customer.customer_id, old_tier, new_tier, "Upgrade"
            )

            send_sms(
                customer.phone_number,
                f"Chuc mung! Ban da len hang {new_tier.value}. "
                f"Diem 3 thang: {points_3m}.",
            )

        elif new_index < current_index:
            # BR-16: Downgrade — chỉ thông báo, áp dụng tháng sau
            send_sms(
                customer.phone_number,
                f"Canh bao: Diem 3 thang cua ban la {points_3m}. "
                f"Hang {customer.tier_level.value} se giam vao ngay 1 thang sau.",
            )
            downgraded += 1

    return {"upgraded": upgraded, "downgraded_warning": downgraded}


def run_point_expiry_check(db: Session) -> int:
    """
    FR-10: Kiểm tra và xử lý điểm hết hạn hàng ngày.
    BR-14: điểm hết hạn sau 12 tháng.
    BR-18: thông báo 30 ngày trước khi hết hạn.
    """
    today = date.today()
    warning_date = today + timedelta(days=30)
    expired_count = 0

    # Lấy điểm hết hạn hôm nay
    expiring_today = (
        db.query(CustomerPoint)
        .filter(
            CustomerPoint.expiry_date == today,
            CustomerPoint.transaction_type == PointTransactionType.EARN,
        )
        .all()
    )

    for point in expiring_today:
        customer = db.query(Customer).filter(
            Customer.customer_id == point.customer_id
        ).first()
        if not customer:
            continue

        expire_amount = point.points_delta
        new_balance = max(0, customer.total_points - expire_amount)

        expire_record = CustomerPoint(
            customer_id=customer.customer_id,
            transaction_type=PointTransactionType.EXPIRE,
            points_delta=-expire_amount,
            balance_after=new_balance,
            notes="Points expired after 12 months",
        )
        db.add(expire_record)
        customer.total_points = new_balance
        expired_count += 1

    db.commit()

    # BR-18: cảnh báo điểm sắp hết hạn trong 30 ngày
    expiring_soon = (
        db.query(CustomerPoint)
        .filter(
            CustomerPoint.expiry_date == warning_date,
            CustomerPoint.transaction_type == PointTransactionType.EARN,
        )
        .all()
    )

    for point in expiring_soon:
        customer = db.query(Customer).filter(
            Customer.customer_id == point.customer_id
        ).first()
        if customer:
            send_sms(
                customer.phone_number,
                f"Canh bao: {point.points_delta} diem cua ban se het han vao {warning_date}. "
                f"Hay su dung truoc khi het han!",
            )

    return expired_count


def award_birthday_bonus(db: Session) -> int:
    """
    FR-13: Thưởng điểm sinh nhật.
    BR-23: chạy ngày 1 hàng tháng, thưởng cho tier >= Silver.
    """
    current_month = datetime.utcnow().month
    bonus_count = 0

    customers = db.query(Customer).filter(
        Customer.date_of_birth.isnot(None),
        Customer.tier_level.in_([TierLevel.SILVER, TierLevel.GOLD, TierLevel.PLATINUM]),
    ).all()

    for customer in customers:
        if customer.date_of_birth.month != current_month:
            continue

        bonus = TIER_BIRTHDAY_BONUS[customer.tier_level]
        if bonus <= 0:
            continue

        new_balance = customer.total_points + bonus
        point_record = CustomerPoint(
            customer_id=customer.customer_id,
            transaction_type=PointTransactionType.BONUS,
            points_delta=bonus,
            balance_after=new_balance,
            expiry_date=date.today() + timedelta(days=365),
            notes="Birthday bonus",
        )
        db.add(point_record)
        customer.total_points = new_balance
        bonus_count += 1

        send_sms(
            customer.phone_number,
            f"Chuc mung sinh nhat! Ban duoc tang {bonus} diem. "
            f"Hang {customer.tier_level.value}.",
        )

    db.commit()
    return bonus_count