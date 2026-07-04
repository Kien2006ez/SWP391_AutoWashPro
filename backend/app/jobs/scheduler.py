"""
Scheduler — M4 (Loyalty Engine / Cron Jobs)
Chạy tự động theo lịch:
- Ngày 1 hàng tháng lúc 00:00: tier review + birthday bonus
- Mỗi ngày lúc 01:00: kiểm tra điểm hết hạn
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

scheduler = BackgroundScheduler(timezone="Asia/Ho_Chi_Minh")


def start_scheduler():
    """Gọi hàm này trong main.py khi khởi động server."""
    from app.db.session import SessionLocal
    from app.services import loyalty_engine

    def monthly_tier_review_job():
        """Chạy ngày 1 hàng tháng lúc 00:00 — FR-09."""
        db = SessionLocal()
        try:
            result = loyalty_engine.run_monthly_tier_review(db)
            print(f"[CRON] Monthly tier review done: {result}")
        finally:
            db.close()

    def birthday_bonus_job():
        """Chạy ngày 1 hàng tháng lúc 00:05 — FR-13."""
        db = SessionLocal()
        try:
            count = loyalty_engine.award_birthday_bonus(db)
            print(f"[CRON] Birthday bonus awarded to {count} customers")
        finally:
            db.close()

    def point_expiry_job():
        """Chạy mỗi ngày lúc 01:00 — FR-10."""
        db = SessionLocal()
        try:
            count = loyalty_engine.run_point_expiry_check(db)
            print(f"[CRON] Point expiry check done: {count} points expired")
        finally:
            db.close()

    # Ngày 1 hàng tháng lúc 00:00 — Tier Review
    scheduler.add_job(
        monthly_tier_review_job,
        trigger=CronTrigger(day=1, hour=0, minute=0),
        id="monthly_tier_review",
        replace_existing=True,
    )

    # Ngày 1 hàng tháng lúc 00:05 — Birthday Bonus
    scheduler.add_job(
        birthday_bonus_job,
        trigger=CronTrigger(day=1, hour=0, minute=5),
        id="birthday_bonus",
        replace_existing=True,
    )

    # Mỗi ngày lúc 01:00 — Point Expiry
    scheduler.add_job(
        point_expiry_job,
        trigger=CronTrigger(hour=1, minute=0),
        id="point_expiry_check",
        replace_existing=True,
    )

    scheduler.start()
    print("[CRON] Scheduler started — 3 jobs registered")