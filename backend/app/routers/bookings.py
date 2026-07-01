from fastapi import APIRouter
from fastapi import HTTPException
from pydantic import BaseModel

from app.services.booking_service import (
    get_all_bookings,
    create_booking,
    update_booking,
    delete_booking
)

router = APIRouter(
    prefix="/bookings",
    tags=["Bookings"]
)


class BookingRequest(BaseModel):
    customer: str
    service: str
    booking_date: str


@router.get("")
def get_all():

    return get_all_bookings()


@router.get("/{booking_id}")
def get_one(
    booking_id: int
):

    booking = get_booking_by_id(
        booking_id
    )

    if booking is None:
        raise HTTPException(
            status_code=404,
            detail="Booking not found"
        )

    return booking


@router.post("")
def create(
    data: BookingRequest
):

    return create_booking(
        data.customer,
        data.service,
        data.booking_date
    )


@router.put("/{booking_id}")
def update(
    booking_id: int,
    data: BookingRequest
):

    booking = update_booking(
        booking_id,
        data.dict()
    )

    if booking is None:
        raise HTTPException(
            status_code=404,
            detail="Booking not found"
        )

    return booking


@router.delete("/{booking_id}")
def delete(
    booking_id: int
):

    booking = delete_booking(
        booking_id
    )

    if booking is None:
        raise HTTPException(
            status_code=404,
            detail="Booking not found"
        )

    return {
        "message": "Deleted successfully"
    }