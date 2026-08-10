"""
Face Recognition v2 - YOLOv8 + ORB Feature-Based Implementation
Uses YOLOv8 for robust face detection and ORB for embeddings
"""

import os
import cv2
import numpy as np
from pathlib import Path
from datetime import datetime, UTC
from ultralytics import YOLO

# Configuration
KNOWN_FACES_DIR = Path("data/known_faces")
KNOWN_FACES_DIR.mkdir(parents=True, exist_ok=True)
INTRUSIONS_DIR = Path("data/intruder_snaps")
INTRUSIONS_DIR.mkdir(parents=True, exist_ok=True)

# Initialize YOLOv8 Face Detector
try:
    face_detector = YOLO("yolov8n-face.pt")
    print("✅ YOLOv8 Face Detector Loaded Successfully")
except Exception as e:
    print(f"⚠️ YOLOv8 initialization failed: {e}")
    face_detector = None

# Initialize ORB (OpenCV feature extractor)
try:
    ORB = cv2.ORB_create(nfeatures=500)
    print("✅ OpenCV ORB Feature Detector Loaded Successfully")
except Exception as e:
    print(f"⚠️ ORB initialization failed: {e}")
    ORB = None


def extract_face_region(frame: np.ndarray) -> tuple[np.ndarray | None, tuple | None]:
    """Extract face region from frame using YOLOv8"""
    try:
        if face_detector is None:
            return None, None
        
        # Run YOLOv8 inference
        results = face_detector(frame, verbose=False)
        
        if len(results) == 0 or results[0].boxes is None or len(results[0].boxes) == 0:
            return None, None
        
        # Get the first (most confident) detection
        boxes = results[0].boxes
        if len(boxes) == 0:
            return None, None
        
        # Get coordinates of the first box
        box = boxes[0]
        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
        
        # Ensure coordinates are within frame bounds
        x1 = max(0, x1)
        y1 = max(0, y1)
        x2 = min(frame.shape[1], x2)
        y2 = min(frame.shape[0], y2)
        
        face_region = frame[y1:y2, x1:x2]
        
        if face_region.size > 0:
            return face_region, (x1, y1, x2, y2)
        
        return None, None
    
    except Exception as e:
        print(f"Face detection error: {e}")
        return None, None


def extract_embedding(frame: np.ndarray) -> np.ndarray | None:
    """Extract face embedding using ORB features"""
    face_region, _ = extract_face_region(frame)
    
    if face_region is None:
        return None
    
    try:
        # Convert to grayscale for ORB
        gray = cv2.cvtColor(face_region, cv2.COLOR_BGR2GRAY)
        
        # Resize to consistent size
        resized = cv2.resize(gray, (128, 128))
        
        # Extract ORB keypoints and descriptors
        kp, des = ORB.detectAndCompute(resized, None)
        
        if des is None or len(des) == 0:
            # Fallback: use raw pixel histogram
            hist = cv2.calcHist([resized], [0], None, [256], [0, 256])
            embedding = hist.flatten().astype(np.float32)
            return embedding / (np.linalg.norm(embedding) + 1e-8)
        
        # Convert descriptors to embedding
        embedding = des.astype(np.float32).flatten()
        
        # Normalize
        norm = np.linalg.norm(embedding)
        if norm == 0:
            return None
        
        return embedding / norm
    
    except Exception as e:
        print(f"❌ Embedding extraction error: {e}")
        return None


def save_embedding(name: str, embedding: np.ndarray) -> bool:
    """Save face embedding to file"""
    try:
        filepath = KNOWN_FACES_DIR / f"{name}.npy"
        np.save(filepath, embedding)
        print(f"✅ Saved embedding: {filepath}")
        return True
    except Exception as e:
        print(f"❌ Save embedding error: {e}")
        return False


def load_embeddings() -> tuple[np.ndarray, list[str]]:
    """Load all known face embeddings"""
    embeddings = []
    names = []
    
    for file in KNOWN_FACES_DIR.glob("*.npy"):
        try:
            emb = np.load(file)
            embeddings.append(emb)
            names.append(file.stem)
        except Exception as e:
            print(f"⚠️ Failed to load {file}: {e}")
    
    if len(embeddings) == 0:
        return np.array([]), []
    
    # Pad embeddings to same size
    max_size = max(len(e) for e in embeddings)
    padded = []
    for emb in embeddings:
        if len(emb) < max_size:
            emb = np.pad(emb, (0, max_size - len(emb)), mode='constant')
        padded.append(emb[:max_size])
    
    return np.array(padded), names


def match_face(known_embeddings: np.ndarray, known_names: list[str], 
               test_embedding: np.ndarray, threshold: float = 0.5) -> tuple[bool, str, float]:
    """Match test embedding against known faces using cosine similarity"""
    if known_embeddings is None or len(known_embeddings) == 0:
        return False, "UNKNOWN", 999.0
    
    if test_embedding is None:
        return False, "NO_FACE", 999.0
    
    # Pad test embedding to match known embeddings size
    if len(test_embedding) < len(known_embeddings[0]):
        test_embedding = np.pad(test_embedding, 
                               (0, len(known_embeddings[0]) - len(test_embedding)), 
                               mode='constant')
    else:
        test_embedding = test_embedding[:len(known_embeddings[0])]
    
    # Cosine similarity
    similarities = []
    for known_emb in known_embeddings:
        # Cosine similarity: dot product / (norm1 * norm2)
        norm1 = np.linalg.norm(known_emb)
        norm2 = np.linalg.norm(test_embedding)
        
        if norm1 == 0 or norm2 == 0:
            sim = 0
        else:
            sim = np.dot(known_emb, test_embedding) / (norm1 * norm2)
        
        similarities.append(sim)
    
    best_idx = np.argmax(similarities)
    best_score = similarities[best_idx]
    best_name = known_names[best_idx]
    
    # Higher score = better match (we use similarity, not distance)
    if best_score > threshold:
        return True, best_name, best_score
    else:
        return False, "INTRUDER", 1.0 - best_score


def get_known_faces_count() -> int:
    """Get number of registered known faces"""
    return len(list(KNOWN_FACES_DIR.glob("*.npy")))


def get_known_faces_list() -> list[str]:
    """Get list of known face names"""
    return [f.stem for f in KNOWN_FACES_DIR.glob("*.npy")]


def detect_faces_in_frame(frame: np.ndarray) -> list[tuple]:
    """Detect all faces in frame using YOLOv8"""
    try:
        if face_detector is None:
            return []
        
        # Run YOLOv8 inference
        results = face_detector(frame, verbose=False)
        
        if len(results) == 0 or results[0].boxes is None or len(results[0].boxes) == 0:
            return []
        
        # Extract all detections
        boxes = results[0].boxes
        detections = []
        
        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
            
            # Ensure coordinates are within frame bounds
            x1 = max(0, x1)
            y1 = max(0, y1)
            x2 = min(frame.shape[1], x2)
            y2 = min(frame.shape[0], y2)
            
            if x2 > x1 and y2 > y1:  # Valid region
                detections.append((x1, y1, x2, y2))
        
        return detections
    
    except Exception as e:
        print(f"Face detection error: {e}")
        return []


print("✅ Face Recognition V2 Module Loaded (YOLOv8 + ORB)")
