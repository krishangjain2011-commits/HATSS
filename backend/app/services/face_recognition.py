"""Face recognition service using MediaPipe."""

import os
import cv2
import numpy as np
from pathlib import Path
from datetime import datetime, UTC

# Configuration
MODEL_PATH = "face_landmarker.task"
KNOWN_FACES_DIR = Path("data/known_faces")
KNOWN_FACES_DIR.mkdir(parents=True, exist_ok=True)

# Try to initialize MediaPipe - if it fails, continue with mock
try:
    import mediapipe as mp
    BaseOptions = mp.tasks.python.BaseOptions
    FaceLandmarker = mp.tasks.python.vision.FaceLandmarker
    FaceLandmarkerOptions = mp.tasks.python.vision.FaceLandmarkerOptions
    VisionRunningMode = mp.tasks.python.vision.RunningMode
    
    if os.path.exists(MODEL_PATH):
        options = FaceLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=MODEL_PATH),
            running_mode=VisionRunningMode.IMAGE,
        )
        face_landmarker = FaceLandmarker.create_from_options(options)
    else:
        face_landmarker = None
        print(f"⚠️  Model file not found at {MODEL_PATH}, running in mock mode")
except Exception as e:
    print(f"⚠️  MediaPipe initialization failed: {e}, running in mock mode")
    face_landmarker = None


def extract_embedding(frame: np.ndarray) -> np.ndarray | None:
    """Extract face embedding from frame."""
    if face_landmarker is None:
        # Mock embedding for testing
        return np.random.randn(468 * 3).astype(np.float32)
    
    try:
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        result = face_landmarker.detect(mp_image)
        
        if not result.face_landmarks:
            return None
        
        landmarks = result.face_landmarks[0]
        embedding = []
        for lm in landmarks:
            embedding.extend([lm.x, lm.y, lm.z])
        
        embedding = np.array(embedding, dtype=np.float32)
        
        # Normalize
        norm = np.linalg.norm(embedding)
        if norm == 0:
            return None
        
        return embedding / norm
    except Exception as e:
        print(f"❌ Embedding extraction error: {e}")
        return None


def save_embedding(name: str, embedding: np.ndarray) -> bool:
    """Save face embedding to file."""
    try:
        filepath = KNOWN_FACES_DIR / f"{name}.npy"
        np.save(filepath, embedding)
        print(f"✅ Saved embedding: {filepath}")
        return True
    except Exception as e:
        print(f"❌ Save embedding error: {e}")
        return False


def load_embeddings() -> tuple[np.ndarray, list[str]]:
    """Load all known face embeddings."""
    embeddings = []
    names = []
    
    for file in KNOWN_FACES_DIR.glob("*.npy"):
        try:
            emb = np.load(file)
            embeddings.append(emb)
            names.append(file.stem)
        except Exception as e:
            print(f"⚠️  Failed to load {file}: {e}")
    
    if len(embeddings) == 0:
        return np.array([]), []
    
    return np.array(embeddings), names


def match_face(known_embeddings: np.ndarray, known_names: list[str], 
               test_embedding: np.ndarray, threshold: float = 0.25) -> tuple[bool, str, float]:
    """Match test embedding against known faces."""
    if known_embeddings is None or len(known_embeddings) == 0:
        return False, "UNKNOWN", 999.0
    
    # Euclidean distance
    distances = np.linalg.norm(known_embeddings - test_embedding, axis=1)
    
    best_idx = np.argmin(distances)
    best_score = distances[best_idx]
    best_name = known_names[best_idx]
    
    if best_score < threshold:
        return True, best_name, best_score
    else:
        return False, "INTRUDER", best_score


def get_known_faces_count() -> int:
    """Get number of registered known faces."""
    return len(list(KNOWN_FACES_DIR.glob("*.npy")))


def get_known_faces_list() -> list[str]:
    """Get list of known face names."""
    return [f.stem for f in KNOWN_FACES_DIR.glob("*.npy")]
