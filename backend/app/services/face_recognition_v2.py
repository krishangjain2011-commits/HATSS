"""
Face Recognition v2 - YOLOv8 + Histogram-Based Face Embeddings
Uses YOLOv8 for face detection and normalized face image histogram for embeddings
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
# Using yolov8n.pt (nano) which auto-downloads from Ultralytics
try:
    face_detector = YOLO("yolov8n.pt")
    print("✅ YOLOv8 Detector Loaded Successfully")
except Exception as e:
    print(f"⚠️ YOLOv8 initialization failed: {e}")
    face_detector = None


def extract_face_region(frame: np.ndarray) -> tuple[np.ndarray | None, tuple | None]:
    """Extract face region from frame using YOLOv8"""
    try:
        if face_detector is None:
            return None, None
        
        # Run YOLOv8 inference
        results = face_detector(frame, verbose=False, conf=0.5)
        
        if len(results) == 0 or results[0].boxes is None or len(results[0].boxes) == 0:
            return None, None
        
        # Get the first (most confident) detection that's a person (class 0)
        boxes = results[0].boxes
        if len(boxes) == 0:
            return None, None
        
        # Filter for person class (class 0 in COCO dataset)
        person_boxes = []
        for box in boxes:
            if hasattr(box, 'cls') and box.cls is not None:
                # Class 0 is 'person' in COCO
                if int(box.cls) == 0:
                    person_boxes.append(box)
        
        if len(person_boxes) == 0:
            # Fallback to first detection
            person_boxes = [boxes[0]]
        
        # Get coordinates of the first box
        box = person_boxes[0]
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


def _get_face_histogram_embedding(face_region: np.ndarray) -> np.ndarray:
    """Extract robust face embedding using multiple feature types"""
    try:
        # Resize to standard size for consistent embeddings
        resized = cv2.resize(face_region, (128, 128))
        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
        embeddings = []
        
        # 1. Multi-scale Sobel edge features (texture) - highly discriminative
        for kernel in [3, 5]:
            sobelx = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=kernel)
            sobely = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=kernel)
            magnitude = np.sqrt(sobelx**2 + sobely**2)
            
            # Histogram of edge magnitudes
            hist_mag, _ = np.histogram(magnitude.flatten(), bins=32, range=(0, 500))
            embeddings.extend(hist_mag)
            
            # Edge orientation histogram (HOG-like)
            angle = np.arctan2(sobely, sobelx)
            hist_angle, _ = np.histogram(angle.flatten(), bins=8, range=(-np.pi, np.pi))
            embeddings.extend(hist_angle)
        
        # 2. LAB color histogram - captures color distribution
        lab = cv2.cvtColor(resized, cv2.COLOR_BGR2LAB)
        for ch in range(3):
            hist = cv2.calcHist([lab], [ch], None, [32], [0, 256])
            embeddings.extend(hist.flatten())
        
        # 3. Spatial texture using Canny edges
        edges = cv2.Canny(gray, 50, 150)
        
        # Count edges in regions - spatial structure
        h, w = edges.shape
        regions = [
            edges[:h//2, :w//2].sum(),      # top-left
            edges[:h//2, w//2:].sum(),      # top-right
            edges[h//2:, :w//2].sum(),      # bottom-left
            edges[h//2:, w//2:].sum()       # bottom-right
        ]
        embeddings.extend(regions)
        
        # 4. Intensity histogram from multiple regions (spatial distribution)
        for i in range(4):
            region = gray[i*32:i*32+32, :] if i < 2 else gray[64+(i-2)*32:64+(i-2)*32+32, :]
            hist, _ = np.histogram(region.flatten(), bins=16, range=(0, 256))
            embeddings.extend(hist)
        
        # 5. Histogram of Laplacian (blob detection - captures distinctive features)
        laplacian = cv2.Laplacian(gray, cv2.CV_32F)
        hist_lap, _ = np.histogram(np.abs(laplacian.flatten()), bins=32, range=(0, 1000))
        embeddings.extend(hist_lap)
        
        embedding = np.array(embeddings, dtype=np.float32)
        
        # Normalize to unit vector for Euclidean distance
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
        else:
            embedding = embedding + 1e-8
            embedding = embedding / np.linalg.norm(embedding)
        
        return embedding
    except Exception as e:
        print(f"Error computing embedding: {e}")
        return None


def extract_embedding(frame: np.ndarray) -> np.ndarray | None:
    """Extract face embedding using histogram features"""
    face_region, _ = extract_face_region(frame)
    
    if face_region is None:
        return None
    
    try:
        embedding = _get_face_histogram_embedding(face_region)
        return embedding
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
    """Match test embedding against known faces using Euclidean distance"""
    # If no known embeddings, any face is an intruder
    if known_embeddings is None or len(known_embeddings) == 0:
        return False, "INTRUDER", 0.0
    
    if test_embedding is None:
        return False, "NO_FACE", 0.0
    
    # Ensure test embedding has correct size
    if len(test_embedding) != len(known_embeddings[0]):
        # Pad or truncate to match
        if len(test_embedding) < len(known_embeddings[0]):
            test_embedding = np.pad(test_embedding, 
                                   (0, len(known_embeddings[0]) - len(test_embedding)), 
                                   mode='constant')
        else:
            test_embedding = test_embedding[:len(known_embeddings[0])]
    
    # Calculate Euclidean distances to all known faces
    distances = []
    for known_emb in known_embeddings:
        # Euclidean distance (lower = better match)
        distance = np.linalg.norm(known_emb - test_embedding)
        distances.append(distance)
    
    best_idx = np.argmin(distances)
    best_distance = distances[best_idx]
    best_name = known_names[best_idx]
    
    # Lower distance = better match
    # Threshold of 0.5 means distance must be < 0.5 to match (stricter - requires closer match)
    if best_distance < threshold:
        # Convert distance to confidence (inverse relationship)
        confidence = 1.0 - min(best_distance / threshold, 1.0)
        return True, best_name, confidence
    else:
        # Unknown person (above distance threshold) = intruder
        confidence = min(best_distance / threshold, 1.0)
        return False, "INTRUDER", confidence


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
        results = face_detector(frame, verbose=False, conf=0.5)
        
        if len(results) == 0 or results[0].boxes is None or len(results[0].boxes) == 0:
            return []
        
        # Extract all detections that are persons (class 0)
        boxes = results[0].boxes
        detections = []
        
        for box in boxes:
            # Filter for person class
            if hasattr(box, 'cls') and box.cls is not None and int(box.cls) != 0:
                continue
                
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


def _cleanup_intrusions(max_snaps: int = 30) -> None:
    """Delete all intrusion snaps if count exceeds max_snaps"""
    try:
        if not INTRUSIONS_DIR.exists():
            return
        
        # Count existing snaps (excluding .gitkeep)
        snap_files = [f for f in INTRUSIONS_DIR.glob("*.jpg")]
        count = len(snap_files)
        
        if count > max_snaps:
            # Delete all snaps
            for snap_file in snap_files:
                snap_file.unlink()
            print(f"🧹 Intrusion cleanup: Deleted {count} snaps (exceeded limit of {max_snaps})")
    except Exception as e:
        print(f"⚠️ Intrusion cleanup error: {e}")


def save_intrusion_snap(frame: np.ndarray) -> bool:
    """Save intrusion snapshot and manage cleanup"""
    try:
        INTRUSIONS_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = int(datetime.now(UTC).timestamp())
        intrusion_path = INTRUSIONS_DIR / f"{timestamp}.jpg"
        cv2.imwrite(str(intrusion_path), frame)
        print(f"✅ Intrusion saved: {intrusion_path}")
        
        # Check if cleanup is needed
        _cleanup_intrusions(max_snaps=30)
        
        return True
    except Exception as e:
        print(f"⚠️ Failed to save intrusion: {e}")
        return False


print("✅ Face Recognition V2 Module Loaded (YOLOv8 + Histogram Embeddings)")
