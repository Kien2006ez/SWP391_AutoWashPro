from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from app.dependencies import require_admin
from app.services.admin.promotion_service import (
    get_all_promotions,
    get_promotion_by_id,
    create_promotion,
    update_promotion,
    delete_promotion
)

router = APIRouter(
    prefix="/admin/promotions",
    tags=["Admin - Promotions"],
    dependencies=[Depends(require_admin)]
)


class PromotionRequest(BaseModel):
    code: str
    discount_percent: float
    valid_from: str
    valid_to: str
    description: str


@router.get("")
def list_promotions():
    return get_all_promotions()


@router.get("/{promotion_id}")
def get_one(promotion_id: int):

    promo = get_promotion_by_id(promotion_id)

    if promo is None:
        raise HTTPException(
            status_code=404,
            detail="Promotion not found"
        )

    return promo


@router.post("")
def create(data: PromotionRequest):

    return create_promotion(
        data.code,
        data.discount_percent,
        data.valid_from,
        data.valid_to,
        data.description
    )


@router.put("/{promotion_id}")
def update(promotion_id: int, data: PromotionRequest):

    promo = update_promotion(promotion_id, data.dict())

    if promo is None:
        raise HTTPException(
            status_code=404,
            detail="Promotion not found"
        )

    return promo


@router.delete("/{promotion_id}")
def delete(promotion_id: int):

    promo = delete_promotion(promotion_id)

    if promo is None:
        raise HTTPException(
            status_code=404,
            detail="Promotion not found"
        )

    return {"message": "Promotion deleted successfully"}