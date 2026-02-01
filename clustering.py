import numpy as np
from sklearn.cluster import DBSCAN

class FaceCluster:
    def __init__(self):
        self.embeddings = []
        self.model = None

    def train(self):
        if len(self.embeddings) < 3:
            return
        self.model = DBSCAN(eps=0.08, min_samples=3)
        self.model.fit(self.embeddings)

    def add_embedding(self, emb):
        self.embeddings.append(emb)
        self.train()

    def is_known(self, emb):
        if self.model is None:
            return False

        distances = np.linalg.norm(
            np.array(self.embeddings) - emb, axis=1
        )
        return distances.min() < 0.08
