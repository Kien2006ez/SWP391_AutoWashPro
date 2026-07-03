from typing import Optional

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel

from app.dependencies import require_admin
from app.services.admin.booking_service import (
    get_all_bookings_admin,
    update_booking_status,
    cancel_booking_admin,
    delete_booking_admin
)

router = APIRouter(
    prefix="/admin/bookings",
    tags=["Admin - Bookings"],
    dependencies=[Depends(require_admin)]
)


class StatusUpdateRequest(BaseModel):
    status: str


@router.get("")
def list_bookings(status: Optional[str] = Query(None)):
    return get_all_bookings_admin(status)


@router.put("/{booking_id}/status")
def change_status(booking_id: int, data: StatusUpdateRequest):

    booking = update_booking_status(booking_id, data.status)

    if booking is None:
        raise HTTPException(
            status_code=404,
            detail="Booking not found"
        )

    return booking


@router.put("/{booking_id}/cancel")
def cancel(booking_id: int):

    booking = cancel_booking_admin(booking_id)

    if booking is None:
        raise HTTPException(
            status_code=404,
            detail="Booking not found"
        )

    return booking


@router.delete("/{booking_id}")
def delete(booking_id: int):

    booking = delete_booking_admin(booking_id)

    if booking is None:
        raise HTTPException(
            status_code=404,
            detail="Booking not found"
        )

    return {"message": "Booking deleted successfully"}
