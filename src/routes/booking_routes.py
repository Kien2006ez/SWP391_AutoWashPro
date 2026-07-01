from flask import Blueprint, jsonify
from src.database.db import db
from src.models.booking import Booking

booking_bp = Blueprint('booking', __name__)

# KAN-98: Lịch sử đặt lịch (Booking History API)
@booking_bp.route('/api/bookings', methods=['GET'])
def get_bookings():
    # Lấy toàn bộ dữ liệu từ bảng bookings
    bookings = Booking.query.all()
    result = [{"id": b.id, "status": b.status} for b in bookings]
    
    return jsonify({
        "message": "Lấy danh sách lịch đặt thành công", 
        "data": result
    }), 200

# KAN-99: Hủy lịch (Cancel Booking API)
@booking_bp.route('/api/bookings/<int:booking_id>/cancel', methods=['PUT'])
def cancel_booking(booking_id):
    # Tìm booking theo ID
    booking = Booking.query.get(booking_id)
    
    # Nếu không tìm thấy
    if not booking:
        return jsonify({"message": "Không tìm thấy lịch đặt này!"}), 404
    
    # Nếu lịch đã bị hủy từ trước
    if booking.status == 'cancelled':
        return jsonify({"message": "Lịch này đã bị hủy từ trước rồi!"}), 400

    # Cập nhật trạng thái thành 'cancelled' và lưu vào Database
    booking.status = 'cancelled'
    db.session.commit()
    
    return jsonify({"message": f"Đã hủy thành công lịch đặt mã số {booking_id}"}), 200