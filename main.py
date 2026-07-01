from flask import Flask
from src.database.db import db

# Import các models
from src.models.user import User
from src.models.vehicle import Vehicle
from src.models.booking import Booking

# Import các API routes đã tách riêng
from src.routes.booking_history import history_bp
from src.routes.booking_cancel import cancel_bp

app = Flask(__name__)

# Cấu hình kết nối Database
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+mysqlconnector://root:12345@127.0.0.1/autowashpro"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Khởi tạo DB
db.init_app(app)

# Đăng ký các module API
app.register_blueprint(history_bp)
app.register_blueprint(cancel_bp)

# Tự động tạo bảng
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return "AutoWashPro - Server đã chạy với cấu trúc Modular chuyên nghiệp!"

if __name__ == '__main__':
    app.run(debug=True)