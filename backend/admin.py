from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from passlib.hash import bcrypt

from .models import db, User, FaceEmbedding
from .recognition import extract_face_embeddings_from_image


admin_bp = Blueprint("admin", __name__)


def _require_admin():
    if not current_user.is_authenticated or current_user.role != "teacher":
        return False
    return True


@admin_bp.route("/admin", methods=["GET"]) 
@login_required
def admin_home():
    if not _require_admin():
        return redirect(url_for("auth.login"))
    users = User.query.order_by(User.role.desc(), User.name.asc()).all()
    return render_template("admin.html", users=users)


@admin_bp.route("/admin/create-user", methods=["POST"]) 
@login_required
def admin_create_user():
    if not _require_admin():
        return redirect(url_for("auth.login"))
    name = request.form.get("name")
    email = request.form.get("email")
    student_id = request.form.get("student_id")
    role = request.form.get("role", "student")
    password = request.form.get("password") or "password"
    if role not in ("student", "teacher"):
        role = "student"
    if not name:
        flash("Name is required", "warning")
        return redirect(url_for("admin.admin_home"))
    user = User(name=name, email=email, student_id=student_id, role=role, password_hash=bcrypt.hash(password))
    db.session.add(user)
    db.session.commit()
    flash("User created", "success")
    return redirect(url_for("admin.admin_home"))


@admin_bp.route("/admin/enroll-face/<int:user_id>", methods=["POST"]) 
@login_required
def admin_enroll_face(user_id: int):
    if not _require_admin():
        return redirect(url_for("auth.login"))
    image_file = request.files.get("photo")
    if not image_file or image_file.filename == "":
        flash("No image uploaded", "warning")
        return redirect(url_for("admin.admin_home"))
    embeddings = extract_face_embeddings_from_image(image_file.stream)
    if not embeddings:
        flash("No face detected", "warning")
        return redirect(url_for("admin.admin_home"))
    db.session.add(FaceEmbedding(user_id=user_id, embedding=embeddings[0]))
    db.session.commit()
    flash("Face added", "success")
    return redirect(url_for("admin.admin_home"))


