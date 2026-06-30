import requests
from requests.auth import HTTPBasicAuth
import json

# ============================================================
# CONFIGURATION: ĐIỀN THÔNG TIN TÀI KHOẢN CỦA BẠN TẠI ĐÂY
# ============================================================
DOMAIN_JIRA = "ut-team-washpro"         # Đã cấu hình theo link dự án của nhóm bạn
EMAIL_JIRA = "kienln0272@ut.edu.vn"  # <- THAY EMAIL CỦA BẠN VÀO ĐÂY
API_TOKEN = "YOUR_API_TOKEN_HERE"
PROJECT_KEY = "KAN"                     # Mã dự án mặc định của nhóm bạn

# ============================================================
# SETUP ĐƯỜNG DẪN API VÀ THÔNG TIN XÁC THỰC
# ============================================================
url = f"https://{DOMAIN_JIRA}.atlassian.net/rest/api/3/issue"

headers = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}
auth = HTTPBasicAuth(EMAIL_JIRA, API_TOKEN)

# ============================================================
# DANH SÁCH CÁC TASK CẦN TẠO TỰ ĐỘNG
# ============================================================
task_list = [
    # ========== FEATURE 1: ĐĂNG NHẬP & ĐĂNG KÝ ==========
    {
        "summary": "[F1-DB] Thiết kế schema database cho xác thực người dùng",
        "description": "Tạo bảng Users với các trường: id, email, phone, password_hash, fullname, role (Customer/Admin/Staff), status, created_at, updated_at. Thêm indexes cho email và phone. Tạo bảng OTP_Verification cho xác thực email/SMS.",
        "label": "Database,Feature-1"
    },
    {
        "summary": "[F1-BE] Phát triển API Register (Đăng ký tài khoản)",
        "description": "Xây dựng endpoint POST /api/auth/register nhận email/phone, password, fullname. Validate email format, password strength. Hash password bằng bcrypt. Gửi OTP qua email/SMS. Trả về success/error message.",
        "label": "Backend,Feature-1"
    },
    {
        "summary": "[F1-BE] Phát triển API Verify OTP và Kích hoạt tài khoản",
        "description": "Xây dựng endpoint POST /api/auth/verify-otp nhận email/phone và OTP code. Kiểm tra OTP còn hiệu lực (5 phút), xác thực account trong database.",
        "label": "Backend,Feature-1"
    },
    {
        "summary": "[F1-BE] Phát triển API Login và JWT Token generation",
        "description": "Xây dựng endpoint POST /api/auth/login nhận email/phone và password. Verify password với password_hash. Tạo JWT token (access_token + refresh_token). Trả về user info và token.",
        "label": "Backend,Feature-1"
    },
    {
        "summary": "[F1-BE] Phát triển API Refresh Token và Token validation",
        "description": "Xây dựng endpoint POST /api/auth/refresh-token và middleware xác thực JWT. Kiểm tra token expiration, user status. Trả về new access_token khi hết hạn.",
        "label": "Backend,Feature-1"
    },
    {
        "summary": "[F1-FE] Thiết kế giao diện màn hình Đăng ký (Register Screen)",
        "description": "Tạo form register với input: email/phone, password, confirm password, fullname. Validate client-side realtime. Gọi API register. Hiển thị status verification khi gửi OTP.",
        "label": "Frontend,Feature-1"
    },
    {
        "summary": "[F1-FE] Thiết kế giao diện màn hình Xác thực OTP (Verify OTP Screen)",
        "description": "Tạo form input OTP 6 ký tự với countdown timer 5 phút. Button 'Resend OTP'. Gọi API verify-otp khi nhập đủ ký tự. Redirect sang Login khi thành công.",
        "label": "Frontend,Feature-1"
    },
    {
        "summary": "[F1-FE] Thiết kế giao diện màn hình Đăng nhập (Login Screen)",
        "description": "Tạo form login với input: email/phone, password, remember me checkbox. Gọi API login. Lưu JWT token vào localStorage/sessionStorage. Redirect sang Dashboard.",
        "label": "Frontend,Feature-1"
    },
    {
        "summary": "[F1-TEST] Unit test cho Authentication Backend APIs",
        "description": "Viết test cho register, verify-otp, login endpoints. Mock database. Test cases: valid/invalid email, weak password, expired OTP, wrong password.",
        "label": "Testing,Feature-1"
    },
    {
        "summary": "[F1-TEST] Integration test cho toàn bộ flow Đăng ký & Đăng nhập",
        "description": "Test end-to-end flow: Register -> Verify OTP -> Login -> Receive Token. Kiểm tra state của database sau mỗi bước.",
        "label": "Testing,Feature-1"
    },
    {
        "summary": "[F1-TEST] Frontend UI test cho form Đăng ký & Đăng nhập",
        "description": "Viết test UI kiểm tra validation messages, button states, redirect pages. Test trên nhiều độ phân giải.",
        "label": "Testing,Feature-1"
    },

    # ========== FEATURE 2: ĐẶT LỊCH RỬA XE ==========
    {
        "summary": "[F2-DB] Thiết kế schema database cho Booking & Vehicles",
        "description": "Tạo bảng Vehicles (id, user_id, brand, model, license_plate, color). Tạo bảng Services (id, name, price, duration_minutes, description). Tạo bảng Bookings (id, user_id, vehicle_id, service_id, booking_date, time_slot, status, notes). Thêm indexes cho queries thường xuyên.",
        "label": "Database,Feature-2"
    },
    {
        "summary": "[F2-DB] Thiết kế schema cho Time Slots & Availability",
        "description": "Tạo bảng TimeSlots (id, start_time, end_time, is_available, booking_id). Tạo bảng ScheduleBlocks (id, date, max_bookings_per_slot). Tạo seed data cho 7 ngày tiếp theo.",
        "label": "Database,Feature-2"
    },
    {
        "summary": "[F2-BE] Phát triển API danh sách Services & Pricing",
        "description": "Xây dựng endpoint GET /api/services trả về danh sách tất cả dịch vụ rửa xe với giá, thời gian, mô tả. Hỗ trợ filter, sort, pagination.",
        "label": "Backend,Feature-2"
    },
    {
        "summary": "[F2-BE] Phát triển API danh sách Vehicles của người dùng",
        "description": "Xây dựng endpoint GET /api/vehicles (lấy danh sách xe) và POST /api/vehicles (thêm xe mới). Validate license_plate unique, required fields.",
        "label": "Backend,Feature-2"
    },
    {
        "summary": "[F2-BE] Phát triển API kiểm tra Time Slots trống",
        "description": "Xây dựng endpoint GET /api/bookings/available-slots?date=YYYY-MM-DD trả về danh sách khung giờ trống. Tính toán dựa trên duration service và các booking hiện tại.",
        "label": "Backend,Feature-2"
    },
    {
        "summary": "[F2-BE] Phát triển API Tạo booking mới",
        "description": "Xây dựng endpoint POST /api/bookings nhận vehicle_id, service_id, booking_date, time_slot. Validate: user logged in, vehicle exists, slot available. Tạo record booking với status='pending'.",
        "label": "Backend,Feature-2"
    },
    {
        "summary": "[F2-BE] Phát triển API lấy thông tin Booking chi tiết",
        "description": "Xây dựng endpoint GET /api/bookings/:id trả về booking details + vehicle info + service info + staff assigned. Kiểm tra authorization (user can only view own booking).",
        "label": "Backend,Feature-2"
    },
    {
        "summary": "[F2-BE] Phát triển API hủy hoặc chỉnh sửa Booking",
        "description": "Xây dựng endpoint PATCH /api/bookings/:id (chỉnh sửa date/time nếu >6 giờ trước) và DELETE /api/bookings/:id (hủy booking). Cập nhật status trong database.",
        "label": "Backend,Feature-2"
    },
    {
        "summary": "[F2-FE] Thiết kế màn hình Chọn Dịch vụ (Service Selection)",
        "description": "Hiển thị danh sách dịch vụ dưới dạng cards: tên, giá, thời gian, mô tả. Cho phép click chọn. Lưu selection vào state.",
        "label": "Frontend,Feature-2"
    },
    {
        "summary": "[F2-FE] Thiết kế màn hình Quản lý Xe (Vehicle Management)",
        "description": "Hiển thị danh sách xe của user. Cho phép add/edit/delete. Form add xe: brand, model, license_plate, color. Validate license_plate format.",
        "label": "Frontend,Feature-2"
    },
    {
        "summary": "[F2-FE] Thiết kế màn hình Calendar để chọn ngày & khung giờ",
        "description": "Hiển thị calendar widget cho phép chọn ngày (min hôm nay, max 30 ngày). Khi chọn ngày, load available time slots. Hiển thị slots dưới dạng buttons, disable slots đã hết.",
        "label": "Frontend,Feature-2"
    },
    {
        "summary": "[F2-FE] Thiết kế màn hình Review & Confirm Booking",
        "description": "Hiển thị summary: xe, dịch vụ, ngày, giờ, giá. Cho phép review lại. Button 'Confirm Booking' gọi API. Hiển thị success message hoặc lỗi.",
        "label": "Frontend,Feature-2"
    },
    {
        "summary": "[F2-FE] Thiết kế màn hình danh sách My Bookings",
        "description": "Hiển thị danh sách booking của user dưới dạng list/cards. Phân tab: upcoming, completed, cancelled. Mỗi item show: ngày, giờ, xe, dịch vụ, giá, status. Cho phép click để view detail, hủy booking.",
        "label": "Frontend,Feature-2"
    },
    {
        "summary": "[F2-TEST] Unit test cho Booking Backend APIs",
        "description": "Viết test cho available-slots, create booking, get booking, cancel booking. Mock database. Test cases: invalid date, no slots, double booking.",
        "label": "Testing,Feature-2"
    },
    {
        "summary": "[F2-TEST] Integration test cho toàn bộ flow Đặt lịch",
        "description": "Test end-to-end: Select service -> Choose vehicle -> Pick date/time -> Review -> Confirm booking. Verify database state.",
        "label": "Testing,Feature-2"
    },
    {
        "summary": "[F2-TEST] UI test cho Calendar & Time Slot Selection",
        "description": "Kiểm tra calendar widget, time slot button states, validation messages. Test interaction flow trên multiple devices.",
        "label": "Testing,Feature-2"
    },

    # ========== FEATURE 3: QUẢN LÝ HÓA ĐƠN & THANH TOÁN ==========
    {
        "summary": "[F3-DB] Thiết kế schema database cho Invoices & Payments",
        "description": "Tạo bảng Invoices (id, booking_id, user_id, amount, tax, total, status, issued_date, due_date, paid_date). Tạo bảng Payments (id, invoice_id, amount, payment_method, transaction_id, status, paid_at).",
        "label": "Database,Feature-3"
    },
    {
        "summary": "[F3-DB] Thiết kế schema cho Payment Methods & Integration",
        "description": "Tạo bảng PaymentMethods (id, user_id, type, account_number, is_default). Tạo bảng TransactionLogs (id, invoice_id, payment_id, status, gateway_response, created_at). Thêm seed data payment methods.",
        "label": "Database,Feature-3"
    },
    {
        "summary": "[F3-BE] Phát triển API tự động tạo Invoice khi booking hoàn thành",
        "description": "Xây dựng service/function gọi khi booking status change thành 'completed'. Tính toán amount = service_price + tax. Tạo record Invoice. Gửi email invoice cho user.",
        "label": "Backend,Feature-3"
    },
    {
        "summary": "[F3-BE] Phát triển API lấy danh sách Invoices của user",
        "description": "Xây dựng endpoint GET /api/invoices lấy danh sách hóa đơn của user. Hỗ trợ filter: status (paid/unpaid/overdue), date range. Hỗ trợ pagination, sort.",
        "label": "Backend,Feature-3"
    },
    {
        "summary": "[F3-BE] Phát triển API chi tiết Invoice và tải PDF",
        "description": "Xây dựng endpoint GET /api/invoices/:id trả về invoice details. Endpoint GET /api/invoices/:id/download-pdf để download hóa đơn PDF.",
        "label": "Backend,Feature-3"
    },
    {
        "summary": "[F3-BE] Tích hợp Payment Gateway (VNPay/Stripe/Momo)",
        "description": "Xây dựng service integrate với payment gateway. Hỗ trợ tạo payment URL, xác thực callback từ gateway. Cập nhật status Invoice/Payment khi thanh toán thành công.",
        "label": "Backend,Feature-3"
    },
    {
        "summary": "[F3-BE] Phát triển API Initiate Payment (bắt đầu thanh toán)",
        "description": "Xây dựng endpoint POST /api/payments/initiate nhận invoice_id, payment_method. Tạo Payment record. Trả về payment URL hoặc payment info cho frontend.",
        "label": "Backend,Feature-3"
    },
    {
        "summary": "[F3-BE] Phát triển API Verify Payment Callback từ Gateway",
        "description": "Xây dựng endpoint POST /api/payments/callback để nhận callback từ payment gateway. Verify signature, cập nhật Invoice/Payment status, gửi confirmation email.",
        "label": "Backend,Feature-3"
    },
    {
        "summary": "[F3-BE] Phát triển API refund/hoàn tiền khi hủy booking",
        "description": "Xây dựng logic refund: khi user hủy booking <6 giờ. Tạo refund request, call payment gateway refund API, update Payment status, send notification.",
        "label": "Backend,Feature-3"
    },
    {
        "summary": "[F3-FE] Thiết kế màn hình danh sách Invoices (Invoice List)",
        "description": "Hiển thị danh sách hóa đơn dưới dạng table/cards. Columns: Invoice#, Date, Amount, Status (badge), Actions. Hỗ trợ filter, sort, search. Button view detail, download PDF.",
        "label": "Frontend,Feature-3"
    },
    {
        "summary": "[F3-FE] Thiết kế màn hình chi tiết Invoice (Invoice Detail)",
        "description": "Hiển thị invoice details: invoice number, date, service details, amount breakdown (subtotal, tax, total), payment status. Button 'Pay Now', 'Download PDF', 'Email'. Back button.",
        "label": "Frontend,Feature-3"
    },
    {
        "summary": "[F3-FE] Thiết kế màn hình chọn Payment Method",
        "description": "Hiển thị danh sách payment methods (Credit Card, Bank Transfer, E-Wallet). Radio button để chọn. Option để add new payment method. Button 'Proceed to Payment'.",
        "label": "Frontend,Feature-3"
    },
    {
        "summary": "[F3-FE] Thiết kế màn hình Payment Processing & Confirmation",
        "description": "Redirect user đến payment gateway. Sau thanh toán, show success/error message. Hiển thị order summary + transaction details. Button back to invoices.",
        "label": "Frontend,Feature-3"
    },
    {
        "summary": "[F3-FE] Thiết kế Dashboard analytics cho Admin (Revenue & Payments)",
        "description": "Hiển thị stats: total revenue, pending invoices, completed payments, today's earnings. Charts: revenue trend, payment method breakdown. Danh sách recent transactions.",
        "label": "Frontend,Feature-3"
    },
    {
        "summary": "[F3-TEST] Unit test cho Invoice & Payment Backend APIs",
        "description": "Viết test cho create invoice, get invoices, payment initiation. Mock payment gateway. Test cases: invalid invoice, duplicate payment, refund logic.",
        "label": "Testing,Feature-3"
    },
    {
        "summary": "[F3-TEST] Integration test cho Payment Flow",
        "description": "Test end-to-end: Complete booking -> Auto create invoice -> Initiate payment -> Receive callback -> Update status. Verify email notifications.",
        "label": "Testing,Feature-3"
    },
    {
        "summary": "[F3-TEST] Security test cho Payment Integration",
        "description": "Test HTTPS, signature verification, token validation. Test XSS/CSRF protection. Verify sensitive data not logged.",
        "label": "Testing,Feature-3"
    },
    {
        "summary": "[F3-TEST] UI test cho Payment & Invoice Screens",
        "description": "Kiểm tra invoice list, detail view, payment methods, payment processing screens. Test responsive design, error messages.",
        "label": "Testing,Feature-3"
    }
]

# ============================================================
# VÒNG LẶP TỰ ĐỘNG GỌI API ĐỂ BẮN TASK LÊN JIRA
# ============================================================
print("🚀 Bắt đầu quá trình tự động hóa tạo task lên Jira...")
print("-" * 60)

for task in task_list:
    payload = json.dumps({
        "fields": {
            "project": {
                "key": PROJECT_KEY
            },
            "summary": task["summary"],
            "description": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": task["description"]
                            }
                        ]
                    }
                ]
            },
            "issuetype": {
                "name": "Task"
            },
            "labels": task["label"].split(",")
        }
    })

    response = requests.request("POST", url, data=payload, headers=headers, auth=auth)
    if response.status_code == 201:
        res_data = response.json()
        print(f"✅ Thành công! Đã tạo Task: {task['summary']} -> Mã Ticket: {res_data['key']}")
    else:
        print(f"❌ Thất bại khi tạo: {task['summary']}")
        print(f"   Chi tiết lỗi hệ thống: {response.status_code} - {response.text}")

print("-" * 60)
print("🎉 Quá trình chạy script hoàn tất! Hãy F5 lại trang Jira để xem kết quả tại Board nhé.")