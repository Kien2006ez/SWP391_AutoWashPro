from flask import Blueprint, jsonify
from src.database.db import db
from src.models.booking import Booking

cancel_bp = Blueprint('cancel', __name__)

@cancel_bp.route('/api/bookings/<int:booking_id>/cancel', methods=['PUT'])
def cancel_booking(booking_id):
    booking = Booking.query.get(booking_id)
    if not booking:
        return jsonify({"message": "Không tìm thấy lịch đặt này!"}), 404
    if booking.status == 'cancelled':
        return jsonify({"message": "Lịch này đã bị hủy từ trước rồi!"}), 400

    booking.status = 'cancelled'
    db.session.commit()
    return jsonify({"message": f"Đã hủy thành công lịch đặt mã số {booking_id}"}), 200