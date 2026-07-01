from flask import Flask
from src.database.db import db

# Import các models để SQLAlchemy nhận diện và tự động tạo bảng
from src.models.user import User
from src.models.vehicle import Vehicle
from src.models.booking import Booking

# Import các API routes
from src.routes.booking_routes import booking_bp

app = Flask(__name__)

# Gán trực tiếp cấu hình kết nối MySQL (bỏ qua việc đọc file .env)
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+mysqlconnector://root:12345@127.0.0.1/autowashpro"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Khởi tạo Database với ứng dụng Flask
db.init_app(app)

# Đăng ký API của Booking
app.register_blueprint(booking_bp)

# Tự động tạo bảng trong MySQL nếu chưa có
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return "AutoWashPro xin chào! API đang hoạt động và Database đã được khởi tạo thành công."

if __name__ == '__main__':
    app.run(debug=True)