from flask import Blueprint, jsonify
from src.models.booking import Booking

history_bp = Blueprint('history', __name__)

@history_bp.route('/api/bookings', methods=['GET'])
def get_bookings():
    bookings = Booking.query.all()
    result = [{"id": b.id, "status": b.status} for b in bookings]
    return jsonify({"message": "Lấy danh sách lịch đặt thành công", "data": result}), 200