import numpy as np
from typing import List, Dict, Union, Optional
from sklearn.cluster import DBSCAN
import hdbscan


class EmbeddingClustering:
    """
    A class containing classmethods for clustering and analyzing face embeddings.
    Supports HDBSCAN and DBSCAN, and computes prototype vectors for each cluster.
    """
    @classmethod
    def cosine(cls, a, b):
        return 1 - np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    @classmethod
    def euclidean(cls, a, b):
        return np.linalg.norm(a - b)

    @classmethod
    def fit_hdbscan(
        cls,
        embeddings: Union[List[np.ndarray], np.ndarray],
        min_cluster_size: int = 5,
        metric: str = "euclidean"
    ) -> np.ndarray:
        embeddings = np.array(embeddings)
        clusterer = hdbscan.HDBSCAN(min_cluster_size=min_cluster_size, metric=metric)
        labels = clusterer.fit_predict(embeddings)
        return labels

    @classmethod
    def fit_dbscan(
        cls,
        embeddings: Union[List[np.ndarray], np.ndarray],
        eps: float = 0.5,
        min_samples: int = 3,
        metric: str = "euclidean"
    ) -> np.ndarray:
        embeddings = np.array(embeddings)
        clusterer = DBSCAN(eps=eps, min_samples=min_samples, metric=metric)
        labels = clusterer.fit_predict(embeddings)
        return labels

    @classmethod
    def get_cluster_map(cls, labels: np.ndarray) -> Dict[int, List[int]]:
        cluster_map = {}
        for idx, label in enumerate(labels):
            cluster_map.setdefault(label, []).append(idx)
        return cluster_map

    @classmethod
    def get_cluster_count(cls, labels: np.ndarray) -> int:
        return len(set(labels)) - (1 if -1 in labels else 0)

    @classmethod
    def get_cluster_prototypes(
        cls,
        embeddings: Union[List[np.ndarray], np.ndarray],
        labels: np.ndarray
    ) -> Dict[int, np.ndarray]:
        embeddings = np.array(embeddings)
        cluster_map = cls.get_cluster_map(labels)
        prototypes = {}
        for label, indices in cluster_map.items():
            if label == -1:
                continue
            try:
                cluster_embeddings = embeddings[indices]
                prototype = np.mean(cluster_embeddings, axis=0)
                prototypes[label] = prototype
            except Exception as e:
                print(f"[Warning] Could not compute prototype for cluster {label}: {e}")
        return prototypes

    @classmethod
    def compute_prototypes(
        cls,
        embeddings_by_label: Dict[Union[int, str], List[np.ndarray]]
    ) -> Dict[Union[int, str], np.ndarray]:
        """
        Compute average (prototype) embedding for each class or cluster.

        Args:
            embeddings_by_label (dict): A dictionary mapping class or cluster labels
                                        to a list of embedding vectors.

        Returns:
            dict: A dictionary mapping each label to its average prototype embedding.
                  Labels with empty or invalid embedding lists are skipped with warnings.
        """
        prototypes = {}
        for label, vectors in embeddings_by_label.items():
            try:
                arr = np.array(vectors)
                if arr.ndim != 2 or arr.shape[0] == 0:
                    raise ValueError("Invalid embedding shape")
                prototypes[label] = np.mean(arr, axis=0)
            except Exception as e:
                print(f"[Warning] Could not compute prototype for label '{label}': {e}")
        return prototypes

    @classmethod
    def predict_nearest_cluster(cls, embedding: np.ndarray, prototypes: Dict[Union[int, str], np.ndarray], metric: str = "cosine") -> int:
        """
        Predicts the closest cluster for a new embedding based on cluster prototypes.

        Returns:
            int: Closest cluster label.
        """
        if metric == "cosine":
            dist_fn = cls.cosine
        elif metric == "euclidean":
            dist_fn = cls.euclidean
        else:
            raise ValueError("Unsupported metric: choose 'cosine' or 'euclidean'")

        best_label = -1
        min_dist = float("inf")

        for label, proto in prototypes.items():
            dist = dist_fn(embedding, proto)
            if dist < min_dist:
                min_dist = dist
                best_label = label

        return best_label

