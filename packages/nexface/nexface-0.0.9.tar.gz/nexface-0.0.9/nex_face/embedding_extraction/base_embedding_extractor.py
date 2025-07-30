import os
import pickle
from typing import Dict, List
import numpy as np

class BaseEmbeddingExtraction:
    def save_embeddings(self, embeddings: List[np.ndarray], file_path: str) -> None:
        """
        Save embeddings to file as pkl file.
        """
        try:
            with open(file_path, 'wb') as f:
                pickle.dump(embeddings, f)
        except (OSError, pickle.PickleError) as e:
            raise RuntimeError(f"Error saving embeddings to '{file_path}': {e}") from e

    def load_embeddings(self, file_path: str):
        """
        Load embeddings from file as pkl file.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"No such file: {file_path}")
        try:
            with open(file_path, 'rb') as f:
                embeddings = pickle.load(f)
            return embeddings
        except (OSError, pickle.PickleError) as e:
            raise RuntimeError(f"Error loading embeddings from '{file_path}': {e}") from e