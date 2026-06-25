"""
AutoWashPro - Database Configuration (Đã sửa đổi bởi Project Manager)
Kết nối MySQL bằng SQLAlchemy thông qua mysqlconnector chính thức
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_db(app):
    """Khởi tạo database với Flask app"""

    # 🛠️ ĐÃ SỬA: Thay đổi từ mysql+pymysql sang mysql+mysqlconnector
    # Cách này tận dụng đúng thư viện mysql-connector-python mà nhóm đã cài sẵn!
    app.config.setdefault(
        "SQLALCHEMY_DATABASE_URI",
        "mysql+mysqlconnector://root:@localhost:3306/autowashpro?charset=utf8mb4",
    )
    app.config.setdefault("SQLALCHEMY_TRACK_MODIFICATIONS", False)
    app.config.setdefault("SQLALCHEMY_ECHO", False)  # Hiện log SQL nếu chỉnh True

    # Giữ nguyên cấu hình tối ưu hệ thống của nhóm
    app.config.setdefault(
        "SQLALCHEMY_ENGINE_OPTIONS",
        {
            "pool_recycle": 280,
            "pool_pre_ping": True,
            "pool_size": 10,
            "max_overflow": 20,
        },
    )

    db.init_app(app)
    return db