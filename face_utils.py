import cv2
import mediapipe as mp
import numpy as np

def get_face_embedding(image_path):
    # Read image safely
    image = cv2.imread(image_path)
    if image is None:
        return None

    try:
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    except Exception:
        return None

    try:
        face_detection = mp.solutions.face_detection.FaceDetection(
            model_selection=0,
            min_detection_confidence=0.3
        )

        results = face_detection.process(image_rgb)

        # Close detector properly (important for Streamlit)
        face_detection.close()

        if results is None:
            return None
        if results.detections is None:
            return None
        if len(results.detections) == 0:
            return None

        detection = results.detections[0]

        # Defensive access
        if not hasattr(detection, "location_data"):
            return None
        if not hasattr(detection.location_data, "relative_bounding_box"):
            return None

        bbox = detection.location_data.relative_bounding_box

        # Convert to simple numeric vector
        return np.array([
            float(bbox.xmin),
            float(bbox.ymin),
            float(bbox.width),
            float(bbox.height)
        ])

    except Exception:
        # Never let CV crash the app
        return None
