# Auto_Attendance_System
Face Recognition based Auto Attendance System

This project implements a student-involved workflow:
- Teacher starts an attendance session and streams frames from the webcam.
- Students login (password or OTP) and must be visible in the teacher’s webcam.
- Attendance is marked Present only if both conditions are met.

## Features
- Teacher portal to start/stop session and live scan
- Student portal with login and attendance status
- Face enrollment per student (stores embeddings)
- Cross-verification: student must be logged in AND recognized on camera

## Setup (Windows)
1. Install Python 3.10+ and ensure it is on PATH.
2. Create and activate a virtual environment:
   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
3. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
   Note: Installing `face-recognition` may require build tools. If it fails, search for prebuilt wheels for your Python version.
4. Run the server:
   ```powershell
   python -m backend.app
   ```
5. Open `http://localhost:5000/login` in your browser.

## Seeding Users (one-time)
```python
from backend import create_app
from backend.models import db, User
from passlib.hash import bcrypt
app = create_app()
with app.app_context():
    t = User(name='Teacher', email='teacher@example.com', role='teacher', password_hash=bcrypt.hash('password'))
    s = User(name='Ravi', student_id='S1001', role='student', password_hash=bcrypt.hash('password'))
    db.session.add_all([t, s])
    db.session.commit()
```

## Usage
- Teacher logs in and starts a session at `Teacher` portal; allow camera access.
- Student logs in on phone/laptop and visits `Student` portal; enroll face if needed.
- When the student is both logged in and visible on camera, status becomes Present.

## Notes
- This is a demo; do not use in production without hardening.
- For better performance or reliability, consider using WebRTC and more robust face models.