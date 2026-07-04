from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.deps import get_current_customer
from app.models.customer import Customer
from app.models.loyalty import CustomerPoint
from app.schemas.loyalty_schema import (
    PointTransactionResponse, RedeemPointsRequest,
)
from app.services import loyalty_engine

router = APIRouter()


@router.get("/points", response_model=list[PointTransactionResponse])
def get_point_history(
    customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db),
):
    """FR-08: xem lịch sử điểm."""
    return (
        db.query(CustomerPoint)
        .filter(CustomerPoint.customer_id == customer.customer_id)
        .order_by(CustomerPoint.created_at.desc())
        .limit(50)
        .all()
    )


@router.post("/redeem")
def redeem_points(
    payload: RedeemPointsRequest,
    customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db),
):
    """FR-11: đổi điểm lấy phần thưởng."""
    try:
        loyalty_engine.redeem_points(
            db=db,
            customer=customer,
            points_cost=payload.points_cost,
            reward_description=payload.reward_description,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "message": "Đổi thưởng thành công.",
        "remaining_points": customer.total_points,
    }