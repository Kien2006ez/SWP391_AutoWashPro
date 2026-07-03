from app.services.booking_service import bookings, get_booking_by_id


def get_all_bookings_admin(status: str = None):
    """Return all bookings, optionally filtered by status."""

    if status:
        return [
            b for b in bookings
            if b["status"].lower() == status.lower()
        ]

    return bookings


def update_booking_status(booking_id: int, status: str):

    booking = get_booking_by_id(booking_id)

    if booking is None:
        return None

    booking["status"] = status

    return booking


def cancel_booking_admin(booking_id: int):

    booking = get_booking_by_id(booking_id)

    if booking is None:
        return None

    booking["status"] = "Cancelled"

    return booking


def delete_booking_admin(booking_id: int):

    booking = get_booking_by_id(booking_id)

    if booking:
        bookings.remove(booking)

    return booking
