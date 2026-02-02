from PIL import Image
import mediapipe as mp
import numpy as np

def get_face_embedding(image_path):
    try:
        # Load image using PIL (stable on Streamlit)
        image = Image.open(image_path).convert("RGB")
        image_np = np.array(image)

        mp_face_detection = mp.solutions.face_detection

        with mp_face_detection.FaceDetection(
            model_selection=0,
            min_detection_confidence=0.3
        ) as detector:

            results = detector.process(image_np)

            if not results or not results.detections:
                return None

            bbox = results.detections[0].location_data.relative_bounding_box

            return np.array([
                float(bbox.xmin),
                float(bbox.ymin),
                float(bbox.width),
                float(bbox.height)
            ])

    except Exception:
        return None
