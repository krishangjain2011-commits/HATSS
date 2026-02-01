from sklearn.cluster import DBSCAN
import numpy as np

class FaceCluster:
    def __init__(self):
        self.embeddings = []
        self.model = None

    def train(self, embeddings):
        self.embeddings = np.array(embeddings)
        self.model = DBSCAN(eps=0.6, min_samples=3, metric="euclidean")
        self.model.fit(self.embeddings)

    def is_known(self, new_embedding):
        if self.model is None:
            return False

        distances = np.linalg.norm(self.embeddings - new_embedding, axis=1)
        return min(distances) < 0.6
