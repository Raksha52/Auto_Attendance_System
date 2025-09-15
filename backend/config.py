import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.abspath(os.path.join(os.path.dirname(__file__), 'app.db'))}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "uploads"))
    FACE_MODEL = "hog"  # or 'cnn' if you have dlib GPU


os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

