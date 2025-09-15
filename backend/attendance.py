from datetime import datetime
from typing import Dict
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user

from .models import db, User, ClassSession, Attendance, FaceEmbedding
from .recognition import load_image_cv2, detect_and_crop_faces, train_lbph, predict_lbph


attendance_bp = Blueprint("attendance", __name__)


@attendance_bp.route("/teacher", methods=["GET"]) 
@login_required
def teacher_portal():
    if current_user.role != "teacher":
        return redirect(url_for("attendance.student_portal"))
    session = ClassSession.query.filter_by(teacher_id=current_user.id, is_active=True).order_by(ClassSession.started_at.desc()).first()
    return render_template("teacher.html", session=session)


@attendance_bp.route("/teacher/start", methods=["POST"]) 
@login_required
def start_session():
    if current_user.role != "teacher":
        return jsonify({"ok": False, "error": "Forbidden"}), 403
    active = ClassSession.query.filter_by(teacher_id=current_user.id, is_active=True).first()
    if active:
        return jsonify({"ok": True, "session_id": active.id})
    session = ClassSession(teacher_id=current_user.id, started_at=datetime.utcnow(), is_active=True)
    db.session.add(session)
    db.session.commit()
    return jsonify({"ok": True, "session_id": session.id})


@attendance_bp.route("/teacher/stop", methods=["POST"]) 
@login_required
def stop_session():
    if current_user.role != "teacher":
        return jsonify({"ok": False, "error": "Forbidden"}), 403
    session = ClassSession.query.filter_by(teacher_id=current_user.id, is_active=True).first()
    if not session:
        return jsonify({"ok": False, "error": "No active session"}), 400
    session.is_active = False
    session.ended_at = datetime.utcnow()
    db.session.commit()
    return jsonify({"ok": True})


@attendance_bp.route("/teacher/frame", methods=["POST"]) 
@login_required
def process_frame():
    if current_user.role != "teacher":
        return jsonify({"ok": False, "error": "Forbidden"}), 403
    session = ClassSession.query.filter_by(teacher_id=current_user.id, is_active=True).first()
    if not session:
        return jsonify({"ok": False, "error": "No active session"}), 400

    file = request.files.get("frame")
    if not file:
        return jsonify({"ok": False, "error": "Frame missing"}), 400

    img = load_image_cv2(file.stream)
    faces = detect_and_crop_faces(img)
    if not faces:
        return jsonify({"ok": True, "matches": []})

    # Prepare training data from stored face images
    user_id_to_paths: Dict[int, list] = {}
    # Persist embeddings as temp images for training
    import tempfile, os
    tmpdir = tempfile.mkdtemp(prefix="lbph_")
    try:
        enrolled = FaceEmbedding.query.all()
        for fe in enrolled:
            uid = fe.user_id
            user_id_to_paths.setdefault(uid, [])
            path = os.path.join(tmpdir, f"u{uid}_{fe.id}.png")
            import cv2, numpy as np
            cv2.imwrite(path, np.array(fe.embedding))
            user_id_to_paths[uid].append(path)

        train_faces, train_labels = [], []
        for uid, paths in user_id_to_paths.items():
            for p in paths:
                import cv2
                img_t = cv2.imread(p)
                if img_t is None:
                    continue
                det = detect_and_crop_faces(img_t)
                if not det:
                    continue
                train_faces.append(det[0])
                train_labels.append(int(uid))

        model = train_lbph(train_faces, train_labels)
        preds = predict_lbph(model, faces)

        matches = []
        for (label, confidence) in preds:
            # Lower confidence is better for LBPH. Threshold ~ 70-90 depending on data.
            if confidence <= 75.0:
                user = User.query.get(int(label))
                if user and user.role == "student" and user.is_online:
                    existing = Attendance.query.filter_by(session_id=session.id, student_id=user.id).first()
                    if not existing:
                        record = Attendance(session_id=session.id, student_id=user.id, status="present")
                        db.session.add(record)
                        db.session.commit()
                    matches.append({"student_id": user.student_id, "name": user.name, "confidence": confidence})
        return jsonify({"ok": True, "matches": matches})
    finally:
        try:
            import shutil
            shutil.rmtree(tmpdir)
        except Exception:
            pass


@attendance_bp.route("/student", methods=["GET"]) 
@login_required
def student_portal():
    if current_user.role != "student":
        return redirect(url_for("attendance.teacher_portal"))
    active_session = ClassSession.query.filter_by(is_active=True).order_by(ClassSession.started_at.desc()).first()
    attendance = None
    if active_session:
        attendance = Attendance.query.filter_by(session_id=active_session.id, student_id=current_user.id).first()
    return render_template("student.html", active_session=active_session, attendance=attendance)

