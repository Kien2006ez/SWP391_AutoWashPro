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
