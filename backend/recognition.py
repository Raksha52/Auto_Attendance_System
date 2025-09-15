from typing import List, Tuple, Dict
import io
import os
import numpy as np
from PIL import Image
import cv2


def load_image_cv2(stream_or_bytes) -> np.ndarray:
    if isinstance(stream_or_bytes, (bytes, bytearray)):
        data = bytes(stream_or_bytes)
    else:
        data = stream_or_bytes.read()
    image = Image.open(io.BytesIO(data)).convert("RGB")
    arr = np.array(image)[:, :, ::-1]  # RGB -> BGR for OpenCV
    return arr


def detect_and_crop_faces(image_bgr: np.ndarray, size: Tuple[int, int] = (200, 200)) -> List[np.ndarray]:
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    cascade = cv2.CascadeClassifier(os.path.join(cv2.data.haarcascades, 'haarcascade_frontalface_default.xml'))
    rects = cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5, minSize=(60, 60))
    faces = []
    for (x, y, w, h) in rects:
        face = gray[y:y+h, x:x+w]
        face = cv2.resize(face, size)
        faces.append(face)
    return faces


def load_training_data(user_id_to_image_paths: Dict[int, List[str]]) -> Tuple[List[np.ndarray], List[int]]:
    faces: List[np.ndarray] = []
    labels: List[int] = []
    for user_id, paths in user_id_to_image_paths.items():
        for p in paths:
            try:
                img = cv2.imread(p)
                if img is None:
                    continue
                detected = detect_and_crop_faces(img)
                if not detected:
                    continue
                faces.append(detected[0])
                labels.append(int(user_id))
            except Exception:
                continue
    return faces, labels


def train_lbph(faces: List[np.ndarray], labels: List[int]):
    if not faces:
        return None
    model = cv2.face.LBPHFaceRecognizer_create(radius=1, neighbors=8, grid_x=8, grid_y=8)
    model.train(faces, np.array(labels))
    return model


def predict_lbph(model, faces: List[np.ndarray]) -> List[Tuple[int, float]]:
    predictions: List[Tuple[int, float]] = []
    if model is None:
        return predictions
    for f in faces:
        label, confidence = model.predict(f)
        predictions.append((label, float(confidence)))
    return predictions

