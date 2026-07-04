"""
Research Router — M7 (ML/Data Analyst)
FR-23: Export CSV dữ liệu nghiên cứu
BR-28: Chỉ export anonymized data, không có PII
"""
from datetime import date
from io import StringIO

import pandas as pd
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.deps import get_current_admin
from app.models.admin_user import AdminUser
from app.models.research_log import TransactionLog, TierChangeLog, BookingLog

router = APIRouter()


@router.get("/export/csv")
def export_research_csv(
    from_date: date = Query(..., description="Từ ngày (YYYY-MM-DD)"),
    to_date: date = Query(..., description="Đến ngày (YYYY-MM-DD)"),
    log_type: str = Query(
        default="transaction",
        description="Loại log: transaction | tier_change | booking"
    ),
    admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """
    FR-23: Export dữ liệu nghiên cứu ra CSV.
    BR-28: Chỉ export anonymized data (customer_ref là hash, không có tên/SĐT thật).
    """
    if log_type == "transaction":
        rows = db.query(TransactionLog).filter(
            TransactionLog.created_at >= from_date,
            TransactionLog.created_at <= to_date,
        ).all()

        data = [
            {
                "log_id": str(r.log_id),
                "customer_ref": r.customer_ref,
                "tier_level": r.tier_level.value,
                "service_type": r.service_type.value,
                "amount_vnd": float(r.amount_vnd),
                "points_earned": r.points_earned,
                "points_redeemed": r.points_redeemed,
                "booking_lead_days": r.booking_lead_days,
                "promo_used": r.promo_used,
                "tier_changed": r.tier_changed,
                "created_at": r.created_at.isoformat(),
            }
            for r in rows
        ]
        filename = f"transaction_log_{from_date}_{to_date}.csv"

    elif log_type == "tier_change":
        rows = db.query(TierChangeLog).filter(
            TierChangeLog.created_at >= from_date,
            TierChangeLog.created_at <= to_date,
        ).all()

        data = [
            {
                "log_id": str(r.log_id),
                "customer_ref": r.customer_ref,
                "old_tier": r.old_tier.value,
                "new_tier": r.new_tier.value,
                "reason": r.reason,
                "created_at": r.created_at.isoformat(),
            }
            for r in rows
        ]
        filename = f"tier_change_log_{from_date}_{to_date}.csv"

    elif log_type == "booking":
        rows = db.query(BookingLog).filter(
            BookingLog.created_at >= from_date,
            BookingLog.created_at <= to_date,
        ).all()

        data = [
            {
                "log_id": str(r.log_id),
                "customer_ref": r.customer_ref,
                "tier_at_booking": r.tier_at_booking.value,
                "booking_lead_days": r.booking_lead_days,
                "service_type": r.service_type.value,
                "promo_applied": r.promo_applied,
                "created_at": r.created_at.isoformat(),
            }
            for r in rows
        ]
        filename = f"booking_log_{from_date}_{to_date}.csv"

    else:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=400,
            detail="log_type phải là: transaction | tier_change | booking"
        )

    # Chuyển sang CSV dùng pandas
    df = pd.DataFrame(data)
    output = StringIO()
    df.to_csv(output, index=False, encoding="utf-8-sig")
    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )