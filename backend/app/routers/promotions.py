"""
Promotion Router — M5 (Database Designer)
FR-24: Tạo promotion có target tier
FR-25: Auto-apply promotion khi booking
FR-35: Xem danh sách promotions
"""
from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.deps import get_current_admin, get_current_customer
from app.models.admin_user import AdminUser
from app.models.customer import Customer
from app.models.promotion import SystemPromotion
from app.schemas.loyalty_schema import PromotionCreateRequest, PromotionResponse

router = APIRouter()


# ── FR-24: Tạo promotion ─────────────────────────────────────
@router.post("", response_model=PromotionResponse, status_code=201)
def create_promotion(
    payload: PromotionCreateRequest,
    admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """FR-24: Admin tạo promotion có target tier (ví dụ: Silver+ only)."""
    promo = SystemPromotion(
        title=payload.title,
        promo_type=payload.promo_type,
        value=payload.value,
        target_tier=payload.target_tier,
        start_date=payload.start_date,
        end_date=payload.end_date,
        usage_limit=payload.usage_limit,
        created_by=admin.username,
    )
    db.add(promo)
    db.commit()
    db.refresh(promo)
    return promo


# ── FR-35: Xem danh sách promotions ─────────────────────────
@router.get("", response_model=list[PromotionResponse])
def list_promotions(
    active_only: bool = True,
    admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """FR-35: Admin xem danh sách tất cả promotions."""
    query = db.query(SystemPromotion)
    if active_only:
        query = query.filter(
            SystemPromotion.is_active == True,
            SystemPromotion.end_date >= date.today(),
        )
    return query.order_by(SystemPromotion.created_at.desc()).all()


# ── Deactivate promotion ──────────────────────────────────────
@router.patch("/{promotion_id}/deactivate")
def deactivate_promotion(
    promotion_id: UUID,
    admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Tắt promotion (không xóa, chỉ set is_active=False)."""
    promo = db.query(SystemPromotion).filter(
        SystemPromotion.promotion_id == promotion_id
    ).first()
    if not promo:
        raise HTTPException(status_code=404, detail="Promotion không tồn tại.")
    promo.is_active = False
    db.commit()
    return {"message": "Đã tắt promotion."}


# ── FR-25: Customer xem promotions áp dụng cho tier của mình ──
@router.get("/my-promotions", response_model=list[PromotionResponse])
def get_my_promotions(
    customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db),
):
    """FR-25: Customer xem promotions đang áp dụng cho tier của họ."""
    today = date.today()
    all_promos = db.query(SystemPromotion).filter(
        SystemPromotion.is_active == True,
        SystemPromotion.start_date <= today,
        SystemPromotion.end_date >= today,
    ).all()

    return [
        p for p in all_promos
        if customer.tier_level.value in (p.target_tier or [])
    ]


def get_applicable_promotion(
    db: Session,
    customer: Customer,
) -> SystemPromotion | None:
    """
    FR-25: Lấy promotion tốt nhất áp dụng cho customer.
    BR-25: Nếu có nhiều promotion, chọn cái có value cao nhất.
    Được gọi từ booking flow khi customer checkout.
    """
    today = date.today()
    promos = db.query(SystemPromotion).filter(
        SystemPromotion.is_active == True,
        SystemPromotion.start_date <= today,
        SystemPromotion.end_date >= today,
    ).all()

    eligible = [
        p for p in promos
        if customer.tier_level.value in (p.target_tier or [])
        and (p.usage_limit is None or p.usage_count < p.usage_limit)
    ]

    if not eligible:
        return None

    # BR-25: chọn promotion có value cao nhất
    return max(eligible, key=lambda p: float(p.value))