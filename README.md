### 🚗 SWP391\_AutoWashPro - Automated Car Wash Management System

Hệ thống quản lý tiệm rửa xe tự động và dịch vụ chăm sóc xe chuyên nghiệp - Dự án môn học SWP391.

* * *

### 👥 Project Team Setup & Work Distribution

### 🖥️ Backend Team (Python FastAPI)

*   **M3 (Nhóm trưởng)**: Chịu trách nhiệm Core System bao gồm: Xác thực (`auth`), Đặt lịch (`bookings`), và Quản trị hệ thống (`admin core`). Quản lý các yêu cầu từ FR-01 đến FR-07, FR-18 đến FR-22.
*   **M4**: Chịu trách nhiệm cấu phần logic phức tạp nhất: Hệ thống tính điểm/hạng thành viên (`loyalty engine`) và các tác vụ chạy ngầm tự động (`cron jobs`). Quản lý yêu cầu từ FR-08 đến FR-17.
*   **M5**: Thiết kế cấu trúc cơ sở dữ liệu (`database models`) cho toàn bộ hệ thống và phát triển cấu phần khuyến mãi, mã giảm giá (`promotions module`).

### 🎨 Frontend Team (HTML/CSS/JavaScript thuần)

*   **M1**: Thiết kế giao diện quản trị (`admin dashboard pages`) và chịu trách nhiệm triển khai, cấu hình môi trường hosting (`deploy`).
*   **M2**: Thiết kế toàn bộ giao diện phía khách hàng (`customer-facing pages`) bao gồm: đăng ký/đăng nhập, đặt lịch rửa xe, theo dõi trạng thái và xem điểm thưởng/đổi quà.

### 📊 Research Team

*   **M6**: Thiết kế và triển khai biểu mẫu khảo sát trải nghiệm khách hàng (`survey form`).
*   **M7**: Xây dựng API ghi nhận nhật ký hệ thống (`research API logging`) và sử dụng `Jupyter notebook` phục vụ phân tích dữ liệu hành vi.

* * *

### 📂 Project Structure

text

    SWP391_AutoWashPro/
    │
    ├── backend/                  # Phân hệ Backend (FastAPI)
    │   ├── app/
    │   │   ├── models/           # Cấu trúc bảng Database (M5 phụ trách)
    │   │   ├── routers/          # Điều hướng endpoints API (M3, M4, M5, M7)
    │   │   ├── services/         # Xử lý logic nghiệp vụ chuyên sâu
    │   │   └── main.py           # File khởi chạy chính của API Server
    │   └── requirements.txt      # Các thư viện Python bắt buộc
    │
    ├── frontend/                 # Phân hệ Frontend (HTML5/CSS3/JS)
    │   ├── admin/                # Giao diện dành cho quản lý (M1 phụ trách)
    │   └── customer/             # Giao diện dành cho khách hàng (M2 phụ trách)
    │
    ├── research/                 # Phân hệ nghiên cứu & phân tích dữ liệu
    │   ├── survey/               # Form khảo sát ý kiến khách hàng (M6)
    │   └── notebooks/            # Jupyter notebooks xử lý dữ liệu log (M7)
    │
    └── .venv/                    # Môi trường ảo Python độc lập
    

Hãy thận trọng khi sử dụng mã.

* * *

### 🛠️ Technologies Used

*   **Backend:** Python, FastAPI, SQLAlchemy (ORM)
*   **Database:** MySQL
*   **Frontend:** HTML5, CSS3, JavaScript (Fetch API kết nối hệ thống)
*   **Tools & Management:** GitHub, Jira (Quản lý tiến độ công việc)

* * *

### 🚀 Local Installation & Setup Guide

### 1\. Clone the Repository

Mở VSCode terminal hoặc Command Prompt và chạy lệnh:

bash

    git clone https://github.com/Kien2006ez/SWP391_AutoWashPro.git
    cd SWP391_AutoWashPro
    

Hãy thận trọng khi sử dụng mã.

### 2\. Create Virtual Environment

Khởi tạo một môi trường ảo Python cô lập:

bash

    python -m venv .venv
    

Hãy thận trọng khi sử dụng mã.

### 3\. Activate Virtual Environment

*   **On Windows (CMD):** `.venv\Scripts\activate.bat`
*   **On Windows (PowerShell):** `.venv\Scripts\Activate.ps1`
*   **On macOS/Linux:** `source .venv/bin/activate`

### 4\. Install Required Libraries

Di chuyển vào thư mục backend và tiến hành cài đặt thư viện phụ thuộc:

bash

    cd backend
    pip install -r requirements.txt
    

Hãy thận trọng khi sử dụng mã.

### 5\. Run the API Server

Khởi chạy hệ thống server bằng Uvicorn:

bash

    uvicorn app.main:app --reload
    

Hãy thận trọng khi sử dụng mã.

*Sau khi chạy, truy cập `http://127.0.0` để xem tài liệu tương tác API tự động (Swagger UI).*

* * *

### 🔄 Git Workflow & Team Collaboration

### Before Coding

Luôn luôn lấy mã nguồn mới nhất từ nhánh chính về máy trước khi bắt đầu làm việc để tránh xung đột:

bash

    git pull origin main
    

Hãy thận trọng khi sử dụng mã.

### Development Rules

Các thành viên **không được phép** đẩy code trực tiếp lên nhánh `main`. Mỗi người tự tạo một nhánh tính năng riêng dựa theo mã công việc được giao (Ví dụ: `feature/KAN-11-login`).

### After Coding

Khi hoàn thành một tính năng, thực hiện gom nhóm các thay đổi và đẩy mã nguồn lên:

bash

    git add .
    git commit -m "KAN-xx: mô tả ngắn gọn tính năng vừa làm bằng tiếng Anh"
    

Hãy thận trọng khi sử dụng mã.

*Ví dụ:* `git commit -m "KAN-11: implement login api endpoints"`

Sau đó đẩy nhánh của bạn lên hệ thống và tạo **Pull Request** trên GitHub để Nhóm trưởng duyệt:

bash

    git push origin feature/your-branch-name
    ```
    
