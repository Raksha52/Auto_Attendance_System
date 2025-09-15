from datetime import datetime, timedelta
import os
import random
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from passlib.hash import bcrypt

from .models import db, User, FaceEmbedding
from .recognition import load_image_cv2, detect_and_crop_faces


auth_bp = Blueprint("auth", __name__)


def _generate_otp() -> str:
    return f"{random.randint(100000, 999999)}"


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        identifier = request.form.get("student_id") or request.form.get("email")
        password = request.form.get("password")
        otp = request.form.get("otp")

        user = None
        if identifier and "@" in identifier:
            user = User.query.filter_by(email=identifier).first()
        else:
            user = User.query.filter_by(student_id=identifier).first()

        if not user:
            flash("User not found", "danger")
            return render_template("login.html")

        # Password or OTP based login
        if password:
            if not user.password_hash or not bcrypt.verify(password, user.password_hash):
                flash("Invalid credentials", "danger")
                return render_template("login.html")
        elif otp:
            now = datetime.utcnow()
            if not (user.otp_code and user.otp_expires_at and user.otp_expires_at > now and user.otp_code == otp):
                flash("Invalid or expired OTP", "danger")
                return render_template("login.html")
        else:
            flash("Provide password or OTP", "warning")
            return render_template("login.html")

        login_user(user)
        user.is_online = True
        user.last_login_at = datetime.utcnow()
        # Clear OTP after use
        user.otp_code = None
        user.otp_expires_at = None
        db.session.commit()
        if user.role == "teacher":
            return redirect(url_for("attendance.teacher_portal"))
        return redirect(url_for("attendance.student_portal"))

    return render_template("login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    try:
        u = User.query.get(current_user.id)
        if u:
            u.is_online = False
            db.session.commit()
    finally:
        logout_user()
    return redirect(url_for("auth.login"))


@auth_bp.route("/request-otp", methods=["POST"])  # simplified demo endpoint
def request_otp():
    identifier = request.form.get("student_id") or request.form.get("email")
    user = None
    if identifier and "@" in identifier:
        user = User.query.filter_by(email=identifier).first()
    else:
        user = User.query.filter_by(student_id=identifier).first()
    if not user:
        return jsonify({"ok": False, "error": "User not found"}), 404
    user.otp_code = _generate_otp()
    user.otp_expires_at = datetime.utcnow() + timedelta(minutes=5)
    db.session.commit()
    # In production, send via email/SMS; here we return it for demo
    return jsonify({"ok": True, "otp": user.otp_code})


@auth_bp.route("/enroll", methods=["GET", "POST"])
@login_required
def enroll():
    if request.method == "POST":
        image_file = request.files.get("photo")
        if not image_file or image_file.filename == "":
            flash("No image uploaded", "warning")
            return render_template("enroll.html")
        img = load_image_cv2(image_file.stream)
        faces = detect_and_crop_faces(img)
        if len(faces) == 0:
            flash("No face detected. Try again.", "warning")
            return render_template("enroll.html")
        # Store first detected face image as embedding substitute
        face_embedding = FaceEmbedding(user_id=current_user.id, embedding=faces[0])
        db.session.add(face_embedding)
        db.session.commit()
        flash("Face enrolled successfully", "success")
        return redirect(url_for("attendance.student_portal"))

    return render_template("enroll.html")

