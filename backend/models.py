from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin


db = SQLAlchemy()


class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(64), unique=True, index=True, nullable=True)
    email = db.Column(db.String(120), unique=True, index=True, nullable=True)
    name = db.Column(db.String(120), nullable=False)
    password_hash = db.Column(db.String(255), nullable=True)
    role = db.Column(db.String(20), nullable=False, default="student")  # student or teacher
    otp_code = db.Column(db.String(10), nullable=True)
    otp_expires_at = db.Column(db.DateTime, nullable=True)
    is_online = db.Column(db.Boolean, default=False, nullable=False)
    last_login_at = db.Column(db.DateTime, nullable=True)

    faces = db.relationship("FaceEmbedding", backref="user", lazy=True)


class FaceEmbedding(db.Model):
    __tablename__ = "face_embeddings"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    embedding = db.Column(db.PickleType, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ClassSession(db.Model):
    __tablename__ = "class_sessions"
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    ended_at = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)


class Attendance(db.Model):
    __tablename__ = "attendance"
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey("class_sessions.id"), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    marked_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default="present")  # present/absent

    __table_args__ = (
        db.UniqueConstraint("session_id", "student_id", name="uniq_session_student"),
    )

