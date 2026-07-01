import os
import requests
from requests.auth import HTTPBasicAuth
import json

# ============================================================
# CONFIGURATION: ĐIỀN THÔNG TIN TÀI KHOẢN CỦA BẠN TẠI ĐÂY
# ============================================================
DOMAIN_JIRA = "ut-team-washpro"
EMAIL_JIRA = "kienln0272@ut.edu.vn"
API_TOKEN = "JIRA_API_TOKEN"
PROJECT_KEY = "KAN"

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
    # ========== FEATURE 1: AUTHENTICATION ==========
    {
        "summary": "[F1-DB] User Database Schema",
        "description": "Design and implement database tables for users and OTP verification, including indexes for authentication queries.",
        "label": "Database,Feature-1,M1"
    },
    {
        "summary": "[F1-BE] Register API",
        "description": "Implement POST /api/auth/register with input validation, password hashing, and OTP generation for account verification.",
        "label": "Backend,Feature-1,M3"
    },
    {
        "summary": "[F1-BE] Login API",
        "description": "Implement POST /api/auth/login with credential verification and authentication token issuance.",
        "label": "Backend,Feature-1,M3"
    },
    {
        "summary": "[F1-BE] JWT Authentication Middleware",
        "description": "Add JWT-based authentication middleware to protect private API endpoints and validate token expiration.",
        "label": "Backend,Feature-1,M3"
    },
    {
        "summary": "[F1-FE] Register Page",
        "description": "Create the registration UI with form validation, password confirmation, and OTP verification flow.",
        "label": "Frontend,Feature-1,M2"
    },
    {
        "summary": "[F1-FE] Login Page",
        "description": "Create the login UI with email/phone and password inputs, validation, and token storage handling.",
        "label": "Frontend,Feature-1,M2"
    },

    # ========== FEATURE 2: VEHICLE MANAGEMENT ==========
    {
        "summary": "[F2-DB] Vehicle Database Schema",
        "description": "Design the database schema for vehicles and ensure the relationship with users is correctly modeled.",
        "label": "Database,Feature-2,M5"
    },
    {
        "summary": "[F2-BE] CRUD Vehicle API",
        "description": "Implement create, read, update, and delete APIs for customer vehicle records.",
        "label": "Backend,Feature-2,M5"
    },
    {
        "summary": "[F2-BE] Vehicle Validation",
        "description": "Validate vehicle ownership, required fields, and license plate format before persisting data.",
        "label": "Backend,Feature-2,M5"
    },
    {
        "summary": "[F2-FE] Vehicle Management Page",
        "description": "Build the vehicle management screen for adding, editing, and deleting customer vehicles.",
        "label": "Frontend,Feature-2,M2"
    },
    {
        "summary": "[F2-FE] Customer Profile Page",
        "description": "Create a customer profile page that displays personal information and linked vehicle records.",
        "label": "Frontend,Feature-2,M2"
    },

    # ========== FEATURE 3: BOOKING SYSTEM ==========
    {
        "summary": "[F3-DB] Booking Database Schema",
        "description": "Design the database schema for bookings, services, and related booking metadata.",
        "label": "Database,Feature-3,M3"
    },
    {
        "summary": "[F3-BE] Booking API",
        "description": "Implement the core booking creation endpoint and store booking details in the database.",
        "label": "Backend,Feature-3,M3"
    },
    {
        "summary": "[F3-BE] Booking History API",
        "description": "Expose an API to retrieve the booking history of a customer, including status and timestamps.",
        "label": "Backend,Feature-3,M3"
    },
    {
        "summary": "[F3-BE] Cancel Booking API",
        "description": "Implement the booking cancellation flow with status updates and authorization checks.",
        "label": "Backend,Feature-3,M3"
    },
    {
        "summary": "[F3-BE] Booking Validation Logic",
        "description": "Add validation rules for booking time, service availability, and required business constraints.",
        "label": "Backend,Feature-3,M3"
    },
    {
        "summary": "[F3-BE] Booking Priority Queue",
        "description": "Design and implement the booking priority handling flow for urgent or high-priority appointments.",
        "label": "Backend,Feature-3,M3"
    },
    {
        "summary": "[F3-FE] Booking Page",
        "description": "Build the booking form to select service, vehicle, date, and time slot for appointment creation.",
        "label": "Frontend,Feature-3,M3"
    },
    {
        "summary": "[F3-FE] Booking History Page",
        "description": "Create a page to display customer booking history with filters and status badges.",
        "label": "Frontend,Feature-3,M3"
    },
    {
        "summary": "[F3-TEST] Booking Module Testing",
        "description": "Write unit and integration tests for booking-related backend and UI behaviors.",
        "label": "Testing,Feature-3,M3"
    },

    # ========== FEATURE 4: LOYALTY SYSTEM ==========
    {
        "summary": "[F4-DB] Loyalty Database Schema",
        "description": "Design the loyalty schema including points, tiers, and reward-related entities.",
        "label": "Database,Feature-4,M4"
    },
    {
        "summary": "[F4-BE] Point Calculation Engine",
        "description": "Implement the logic to calculate loyalty points from completed bookings and eligible actions.",
        "label": "Backend,Feature-4,M4"
    },
    {
        "summary": "[F4-BE] Tier Upgrade Engine",
        "description": "Implement automatic tier progression based on accumulated points or completed services.",
        "label": "Backend,Feature-4,M4"
    },
    {
        "summary": "[F4-BE] Reward Redemption API",
        "description": "Implement APIs for redeeming loyalty points for available rewards and updating balances.",
        "label": "Backend,Feature-4,M4"
    },
    {
        "summary": "[F4-BE] Monthly Cron Job",
        "description": "Create the scheduled job to process monthly loyalty updates and reset or recalculate points as needed.",
        "label": "Backend,Feature-4,M4"
    },
    {
        "summary": "[F4-FE] Loyalty Dashboard",
        "description": "Create a dashboard showing loyalty balance, tier status, and recent point activity.",
        "label": "Frontend,Feature-4,M4"
    },
    {
        "summary": "[F4-FE] Reward Page",
        "description": "Build the rewards catalog page so customers can browse and redeem loyalty rewards.",
        "label": "Frontend,Feature-4,M4"
    },
    {
        "summary": "[F4-TEST] Loyalty Testing",
        "description": "Write tests around point awarding, tier upgrades, and reward redemption flows.",
        "label": "Testing,Feature-4,M4"
    },

    # ========== FEATURE 5: PROMOTION ==========
    {
        "summary": "[F5-DB] Promotion Database Schema",
        "description": "Define tables and relationships for promotions, eligibility rules, and applied discounts.",
        "label": "Database,Feature-5,M5"
    },
    {
        "summary": "[F5-BE] Promotion CRUD API",
        "description": "Implement create, read, update, and delete APIs for promotions and discount campaigns.",
        "label": "Backend,Feature-5,M5"
    },
    {
        "summary": "[F5-BE] Target Promotion Logic",
        "description": "Implement promotion applicability logic based on customer segment, booking criteria, and time windows.",
        "label": "Backend,Feature-5,M5"
    },
    {
        "summary": "[F5-FE] Promotion Management Page",
        "description": "Create the administration UI for managing promotional offers and their active periods.",
        "label": "Frontend,Feature-5,M5"
    },
    {
        "summary": "[F5-TEST] Promotion Testing",
        "description": "Write tests for promotion creation, validation, and application rules.",
        "label": "Testing,Feature-5,M5"
    },

    # ========== FEATURE 6: ADMIN DASHBOARD ==========
    {
        "summary": "[F6-BE] Dashboard Statistics API",
        "description": "Expose an admin API for dashboard metrics such as revenue, booking counts, and customer activity.",
        "label": "Backend,Feature-6,M6"
    },
    {
        "summary": "[F6-BE] Customer Management",
        "description": "Implement admin APIs to review, update, and manage customer accounts and statuses.",
        "label": "Backend,Feature-6,M6"
    },
    {
        "summary": "[F6-BE] Booking Management",
        "description": "Implement admin-side booking management APIs for reviewing and updating booking states.",
        "label": "Backend,Feature-6,M6"
    },
    {
        "summary": "[F6-FE] Admin Dashboard UI",
        "description": "Build the administrative dashboard UI with charts, statistics cards, and management sections.",
        "label": "Frontend,Feature-6,M6"
    },

    # ========== FEATURE 7: SURVEY & RESEARCH ==========
    {
        "summary": "[F7-BE] Survey API",
        "description": "Implement APIs to submit survey responses and store feedback for research purposes.",
        "label": "Backend,Feature-7,M7"
    },
    {
        "summary": "[F7-FE] Survey Form UI",
        "description": "Create the customer-facing survey form with rating and comment inputs.",
        "label": "Frontend,Feature-7,M7"
    },
    {
        "summary": "[F7-BE] Analytics Dataset Export",
        "description": "Provide a backend export flow for survey analytics data in a structured format for research use.",
        "label": "Backend,Feature-7,M7"
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