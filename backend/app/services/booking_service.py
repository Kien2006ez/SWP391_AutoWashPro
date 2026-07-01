bookings = []


def get_all_bookings():
    return bookings


def get_booking_by_id(booking_id):

    for booking in bookings:

        if booking["id"] == booking_id:
            return booking

    return None


def create_booking(
    customer,
    service,
    booking_date
):

    booking = {
        "id": len(bookings) + 1,
        "customer": customer,
        "service": service,
        "booking_date": booking_date,
        "status": "Pending"
    }

    bookings.append(booking)

    return booking


def update_booking(
    booking_id,
    new_data
):

    booking = get_booking_by_id(
        booking_id
    )

    if booking is None:
        return None

    booking.update(new_data)

    return booking


def delete_booking(
    booking_id
):

    booking = get_booking_by_id(
        booking_id
    )

    if booking:

        bookings.remove(booking)

    return booking