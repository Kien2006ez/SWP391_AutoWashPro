# SWP391_AutoWashPro

Automated Car Wash Management System - SWP391 Project.

---

# Team Setup Guide

This guide helps team members clone, setup, and run the project correctly on their computers.

---

# 1. Clone the Repository

Open VSCode terminal or command prompt and run:

```bash
git clone https://github.com/Kien2006ez/SWP391_AutoWashPro.git
cd SWP391_AutoWashPro
```

---

# 2. Create Virtual Environment

Create a Python virtual environment:

```bash
python -m venv .venv
```

---

# 3. Activate Virtual Environment

## On Windows

### CMD

```cmd
.venv\Scripts\activate.bat
```

### PowerShell

```powershell
.venv\Scripts\Activate.ps1
```

---

## On macOS/Linux

```bash
source .venv/bin/activate
```

---

# 4. Install Required Libraries

Install all required dependencies:

```bash
pip install -r requirements.txt
```

---

# 5. Run the Project

```bash
python main.py
```

---

# Git Workflow

## Before Coding

Always pull the latest code before starting:

```bash
git pull origin main
```

---

## After Coding

### Add changes

```bash
git add .
```

### Commit changes

```bash
git commit -m "KAN-xx: update feature"
```

Example:

```bash
git commit -m "KAN-11: implement login feature"
```

### Push code to GitHub

```bash
git push origin main
```

---


# Project Structure

```text
SWP391_AutoWashPro/
│
├── main.py
├── requirements.txt
├── README.md
├── .gitignore
├── src/
├── assets/
└── .venv/
```

---
### Bảng Phân Công & Cấu Trúc File Hệ Thống (Frontend & Backend)

| Phân hệ (Mảng) | Thư mục / Tên File | Chức năng chi tiết | Phân công KAN |
| :--- | :--- | :--- | :--- |
| **1. FRONTEND (Giao diện)** | `templates/` | Chứa toàn bộ file giao diện khung xương HTML (`login.html`, `dashboard.html`, `booking.html`...). | Nhóm Frontend |
| | `assets/` | Chứa các file tĩnh để trang trí web (CSS, hình ảnh logo, icon, JavaScript). | Nhóm Frontend |
| **2. BACKEND (Xử lý logic)** | `main.py` | File chạy server chính của hệ thống Flask. Giao tiếp giữa Giao diện và Dữ liệu. | Nhóm Backend |
| | `src/` | Chứa code xử lý logic nghiệp vụ ngầm (kiểm tra mật khẩu, tính toán giờ trống...). | Nhóm Backend |
| | `requirements.txt` | Danh sách các thư viện Python bắt buộc phải cài đặt để chạy dự án. | Cả nhóm |
| **3. DATABASE (Dữ liệu)** | MySQL Database | Hệ quản trị cơ sở dữ liệu lưu thông tin khách hàng, xe, lịch đặt, ưu đãi. | Database Admin |

# Technologies Used

- Python
- Flask
- MySQL
- GitHub
- Jira

---

# Team Workflow

Jira Task
↓
Create Branch
↓
Code Feature
↓
Commit with KAN-xx
↓
Push to GitHub
↓
Review
↓
Done
