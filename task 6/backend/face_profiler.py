import bz2
import os
import urllib.request
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np

try:
    import dlib  # type: ignore
except Exception:  # pragma: no cover
    dlib = None


DLIB_MODEL_URL = "http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2"
DEFAULT_MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "shape_predictor_68_face_landmarks.dat")


class ModelMissingError(Exception):
    pass


def _point_to_int_tuple(point: np.ndarray) -> Tuple[int, int]:
    return int(point[0]), int(point[1])


@dataclass
class FaceProfileResult:
    bounding_box: Dict[str, int]
    key_points: Dict[str, Tuple[int, int]]
    raw_measurements: Dict[str, float]
    normalized_measurements: Dict[str, float]


class FaceProfiler:
    def __init__(self, model_path: str = DEFAULT_MODEL_PATH):
        self.model_path = model_path
        self.detector = None
        self.predictor = None
        self.use_dlib = False

        self.face_cascade = cv2.CascadeClassifier(
            os.path.join(cv2.data.haarcascades, "haarcascade_frontalface_default.xml")
        )
        self.eye_cascade = cv2.CascadeClassifier(
            os.path.join(cv2.data.haarcascades, "haarcascade_eye.xml")
        )
        self.smile_cascade = cv2.CascadeClassifier(
            os.path.join(cv2.data.haarcascades, "haarcascade_smile.xml")
        )

        if dlib is not None and os.path.exists(self.model_path):
            self.detector = dlib.get_frontal_face_detector()
            self.predictor = dlib.shape_predictor(self.model_path)
            self.use_dlib = True

    @staticmethod
    def download_model(destination: str = DEFAULT_MODEL_PATH) -> str:
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        compressed_path = f"{destination}.bz2"
        urllib.request.urlretrieve(DLIB_MODEL_URL, compressed_path)

        with bz2.BZ2File(compressed_path, "rb") as source, open(destination, "wb") as target:
            target.write(source.read())

        os.remove(compressed_path)
        return destination

    @staticmethod
    def _to_np(shape) -> np.ndarray:
        return np.array([[shape.part(i).x, shape.part(i).y] for i in range(68)], dtype=np.float32)

    @staticmethod
    def _distance(p1: np.ndarray, p2: np.ndarray) -> float:
        return float(np.linalg.norm(p1 - p2))

    def _extract_measurements(self, landmarks: np.ndarray, face_rect) -> FaceProfileResult:
        left_eye_center = np.mean(landmarks[36:42], axis=0)
        right_eye_center = np.mean(landmarks[42:48], axis=0)
        nose_top = landmarks[27]
        nose_tip = landmarks[33]
        mouth_left = landmarks[48]
        mouth_right = landmarks[54]
        chin = landmarks[8]
        jaw_left = landmarks[4]
        jaw_right = landmarks[12]

        left_x, top_y, right_x, bottom_y = (
            face_rect.left(),
            face_rect.top(),
            face_rect.right(),
            face_rect.bottom(),
        )
        face_width = float(max(1, right_x - left_x))
        face_height = float(max(1, bottom_y - top_y))

        eye_distance = self._distance(left_eye_center, right_eye_center)
        nose_length = self._distance(nose_top, nose_tip)
        mouth_width = self._distance(mouth_left, mouth_right)
        jaw_width = self._distance(jaw_left, jaw_right)

        raw_measurements = {
            "face_width": round(face_width, 3),
            "face_height": round(face_height, 3),
            "eye_distance": round(eye_distance, 3),
            "nose_length": round(nose_length, 3),
            "mouth_width": round(mouth_width, 3),
            "jaw_width": round(jaw_width, 3),
        }

        normalized_measurements = {
            "eye_to_face_ratio": round(eye_distance / face_width, 4),
            "nose_to_face_ratio": round(nose_length / face_height, 4),
            "mouth_to_face_ratio": round(mouth_width / face_width, 4),
            "jaw_to_face_ratio": round(jaw_width / face_width, 4),
        }

        key_points = {
            "left_eye_center": _point_to_int_tuple(left_eye_center),
            "right_eye_center": _point_to_int_tuple(right_eye_center),
            "nose_tip": _point_to_int_tuple(nose_tip),
            "mouth_left": _point_to_int_tuple(mouth_left),
            "mouth_right": _point_to_int_tuple(mouth_right),
            "chin": _point_to_int_tuple(chin),
        }

        bounding_box = {
            "x": int(left_x),
            "y": int(top_y),
            "width": int(face_width),
            "height": int(face_height),
        }

        return FaceProfileResult(
            bounding_box=bounding_box,
            key_points=key_points,
            raw_measurements=raw_measurements,
            normalized_measurements=normalized_measurements,
        )

    def _profile_with_cascades(self, gray: np.ndarray) -> Dict[str, object]:
        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=6, minSize=(80, 80))
        if len(faces) == 0:
            raise ValueError("No face detected")

        x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
        face_roi_gray = gray[y : y + h, x : x + w]

        eye_detections = self.eye_cascade.detectMultiScale(face_roi_gray, scaleFactor=1.1, minNeighbors=8, minSize=(18, 18))
        eye_centers: List[Tuple[float, float]] = []
        for ex, ey, ew, eh in eye_detections:
            eye_centers.append((x + ex + ew / 2.0, y + ey + eh / 2.0))
        eye_centers = sorted(eye_centers, key=lambda p: p[0])[:2]

        if len(eye_centers) == 2:
            left_eye_center = np.array(eye_centers[0], dtype=np.float32)
            right_eye_center = np.array(eye_centers[1], dtype=np.float32)
            eye_distance = self._distance(left_eye_center, right_eye_center)
        else:
            left_eye_center = np.array([x + 0.32 * w, y + 0.38 * h], dtype=np.float32)
            right_eye_center = np.array([x + 0.68 * w, y + 0.38 * h], dtype=np.float32)
            eye_distance = float(0.36 * w)

        smile_detections = self.smile_cascade.detectMultiScale(face_roi_gray, scaleFactor=1.7, minNeighbors=20, minSize=(25, 25))
        if len(smile_detections) > 0:
            mx, my, mw, mh = max(smile_detections, key=lambda m: m[2] * m[3])
            mouth_left = np.array([x + mx, y + my + mh / 2.0], dtype=np.float32)
            mouth_right = np.array([x + mx + mw, y + my + mh / 2.0], dtype=np.float32)
            mouth_width = float(mw)
        else:
            mouth_left = np.array([x + 0.32 * w, y + 0.75 * h], dtype=np.float32)
            mouth_right = np.array([x + 0.68 * w, y + 0.75 * h], dtype=np.float32)
            mouth_width = float(0.36 * w)

        nose_top = np.array([x + 0.50 * w, y + 0.42 * h], dtype=np.float32)
        nose_tip = np.array([x + 0.50 * w, y + 0.60 * h], dtype=np.float32)
        chin = np.array([x + 0.50 * w, y + h], dtype=np.float32)
        jaw_left = np.array([x + 0.15 * w, y + 0.88 * h], dtype=np.float32)
        jaw_right = np.array([x + 0.85 * w, y + 0.88 * h], dtype=np.float32)

        face_width = float(max(1, w))
        face_height = float(max(1, h))
        nose_length = self._distance(nose_top, nose_tip)
        jaw_width = self._distance(jaw_left, jaw_right)

        raw_measurements = {
            "face_width": round(face_width, 3),
            "face_height": round(face_height, 3),
            "eye_distance": round(float(eye_distance), 3),
            "nose_length": round(nose_length, 3),
            "mouth_width": round(mouth_width, 3),
            "jaw_width": round(jaw_width, 3),
        }

        normalized_measurements = {
            "eye_to_face_ratio": round(float(eye_distance) / face_width, 4),
            "nose_to_face_ratio": round(nose_length / face_height, 4),
            "mouth_to_face_ratio": round(mouth_width / face_width, 4),
            "jaw_to_face_ratio": round(jaw_width / face_width, 4),
        }

        key_points = {
            "left_eye_center": _point_to_int_tuple(left_eye_center),
            "right_eye_center": _point_to_int_tuple(right_eye_center),
            "nose_tip": _point_to_int_tuple(nose_tip),
            "mouth_left": _point_to_int_tuple(mouth_left),
            "mouth_right": _point_to_int_tuple(mouth_right),
            "chin": _point_to_int_tuple(chin),
        }

        return {
            "faces_detected": int(len(faces)),
            "primary_face": {
                "bounding_box": {"x": int(x), "y": int(y), "width": int(w), "height": int(h)},
                "key_points": key_points,
                "raw_measurements": raw_measurements,
                "normalized_measurements": normalized_measurements,
            },
        }

    def profile(self, image_bytes: bytes) -> Dict[str, object]:
        image_array = np.frombuffer(image_bytes, dtype=np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

        if image is None:
            raise ValueError("Invalid image data")

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        if self.use_dlib and self.detector is not None and self.predictor is not None:
            faces = self.detector(gray, 1)

            if not faces:
                raise ValueError("No face detected")

            primary_face = max(faces, key=lambda rect: rect.width() * rect.height())
            shape = self.predictor(gray, primary_face)
            landmarks = self._to_np(shape)

            result = self._extract_measurements(landmarks, primary_face)
            return {
                "faces_detected": len(faces),
                "landmark_backend": "dlib_68",
                "primary_face": {
                    "bounding_box": result.bounding_box,
                    "key_points": result.key_points,
                    "raw_measurements": result.raw_measurements,
                    "normalized_measurements": result.normalized_measurements,
                },
            }

        profile = self._profile_with_cascades(gray)
        profile["landmark_backend"] = "opencv_cascade_fallback"
        return profile


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Manage dlib landmark model")
    parser.add_argument("--download-model", action="store_true", help="Download the 68-point landmark model")
    parser.add_argument("--dest", default=DEFAULT_MODEL_PATH, help="Destination for model file")
    args = parser.parse_args()

    if args.download_model:
        path = FaceProfiler.download_model(args.dest)
        print(f"Model downloaded to: {path}")
    else:
        print("Use --download-model to fetch shape_predictor_68_face_landmarks.dat")
