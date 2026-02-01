from face_utils import get_face_embedding
from clustering import FaceCluster

face_system = FaceCluster()

def add_known_face(image_path):
    emb = get_face_embedding(image_path)
    if emb is not None:
        face_system.add_embedding(emb)
        return True
    return False

def run_detection(image_path):
    emb = get_face_embedding(image_path)

    if emb is None:
        return "No face detected"

    if face_system.is_known(emb):
        return "Known"
    else:
        return "Unknown"
