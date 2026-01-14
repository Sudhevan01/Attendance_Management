# 📋 Attendance Management System (Django)

A web-based Attendance Management System developed using Django that helps administrators manage students, subjects, and attendance efficiently.

---

## 🚀 Features

- Admin login authentication
- Student management
- Subject management
- Attendance marking by subject and date
- Secure access (Admin only)
- Simple and user-friendly interface

---

## 🛠️ Technologies Used

- Backend: Python, Django
- Frontend: HTML, CSS, Bootstrap
- Database: SQLite
- Version Control: Git & GitHub

---

## 📂 Project Structure

attendance_management/
├── attendance_management/          # Project settings
│   ├── __init__.py
│   ├── settings.py                # Django settings
│   ├── urls.py                    # Main URL configuration
│   ├── wsgi.py
│   └── asgi.py
├── attendance/                     # Main application
│   ├── migrations/                # Database migrations
│   ├── templates/
│   │   └── attendance/            # HTML templates
│   │       ├── base.html          # Base template with sidebar
│   │       ├── login.html         # Login page
│   │       ├── dashboard.html     # Dashboard
│   │       ├── student_list.html  # Students list
│   │       ├── student_form.html  # Add/Edit student
│   │       ├── subject_list.html  # Subjects list
│   │       ├── subject_form.html  # Add/Edit subject
│   │       ├── mark_attendance.html        # Mark attendance step 1
│   │       ├── mark_attendance_form.html   # Mark attendance step 2
│   │       ├── view_attendance.html        # View records
│   │       └── attendance_percentage.html  # Percentage report
│   ├── static/
│   │   └── css/
│   │       └── style.css          # Custom styles
│   ├── __init__.py
│   ├── admin.py                   # Admin panel configuration
│   ├── apps.py
│   ├── models.py                  # Database models
│   ├── forms.py                   # Form definitions
│   ├── views.py                   # View functions
│   ├── urls.py                    # App URL configuration
│   └── tests.py                   # Unit tests
├── manage.py                      # Django management script
├── db.sqlite3                     # SQLite database
├── README.md                      # This file


---

## ⚙️ Installation and Setup

1. Clone the repository
```bash
git clone https://github.com/your-username/attendance-management-system.git
cd attendance-management-system
