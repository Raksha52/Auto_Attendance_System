from flask import Flask
from flask_login import LoginManager

from .config import Config
from .models import db, User


login_manager = LoginManager()
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    with app.app_context():
        db.create_all()
        # Auto-seed an admin and sample users on first run
        from passlib.hash import bcrypt
        if User.query.count() == 0:
            admin = User(name="Admin", email="admin@example.com", role="teacher", password_hash=bcrypt.hash("admin123"))
            teacher = User(name="Teacher", email="teacher@example.com", role="teacher", password_hash=bcrypt.hash("password"))
            student = User(name="Ravi", student_id="S1001", role="student", password_hash=bcrypt.hash("password"))
            db.session.add_all([admin, teacher, student])
            db.session.commit()

    from .auth import auth_bp
    from .attendance import attendance_bp
    from .admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(admin_bp)

    from flask import render_template

    @app.route("/")
    def index():
        return render_template("index.html")

    return app

