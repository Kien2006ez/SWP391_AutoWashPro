from flask import Blueprint

booking_bp = Blueprint('booking', __name__)

@booking_bp.route('/api/bookings', methods=['GET'])
def get_bookings():
    return {"message": "Danh sách Booking API đang hoạt động!"}