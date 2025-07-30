"""
FaceRecognition class for predicting face identities based on embeddings.
It uses precomputed embeddings from a known dataset and compares them against
new face embeddings using Euclidean distance (L2 norm) to identify individuals.
"""

import os
from collections import defaultdict
from typing import List, Optional, Tuple
import numpy as np
from nex_face.embedding_extraction.embedding_extractor import EmbeddingExtraction


class FaceRecognition:
    _instance = None

    def __new__(cls, *args, **kwargs):
        """
        Ensures a single instance of FaceRecognition is created (Singleton pattern).

        Returns:
            FaceRecognition: The singleton instance.
        """
        if cls._instance is None:
            cls._instance = super(FaceRecognition, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """
        Initializes the FaceRecognition instance if not already initialized.
        Sets up the embedding extractor and a dictionary to store known embeddings.
        """
        if not hasattr(self, "_initialized"):
            self.embedding_extractor = EmbeddingExtraction()
            self.known_embeddings = defaultdict(list)
            self._initialized = True

    def load_model(self, compile_model: bool = False):
        """
        Loads the FaceNet model for embedding extraction.

        Args:
            compile_model (bool, optional): Whether to compile the model. Defaults to False.

        Raises:
            RuntimeError: If the model fails to load.
        """
        try:
            self.embedding_extractor.load_model(compile_model=compile_model)
        except Exception as e:
            raise RuntimeError(f"Failed to load FaceRecognition model: {e}") from e

    def load_known_embeddings(self, file_path: str):
        """
           Loads known face embeddings from a specified file path.

           Parameters:
               file_path (str): The path to the file containing serialized embeddings (e.g., a .pkl file).

           Raises:
               RuntimeError: If the embeddings cannot be loaded due to an internal error.

           This method updates the `self.known_embeddings` attribute with the loaded embeddings.
           It relies on the `embedding_extractor.load_embeddings` method to deserialize the data.
           """
        try:
            self.known_embeddings = self.embedding_extractor.load_embeddings(file_path)
            if not (isinstance(self.known_embeddings, defaultdict) and self.known_embeddings.default_factory is list):
                raise TypeError("known_embeddings must be of type 'defaultdict(list)'")
        except Exception as e:
            raise RuntimeError(f"Failed to load known embeddings: {e}") from e

    def euclidean_distance(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Computes the Euclidean distance (L2 norm) between two embedding vectors.

        Args:
            embedding1 (np.ndarray): First embedding vector.
            embedding2 (np.ndarray): Second embedding vector.

        Returns:
            float: Euclidean distance between the embeddings.
        """
        return np.linalg.norm(embedding1 - embedding2)

    def predict(self, image: np.ndarray, threshold: float = 0.6) -> List[Tuple[str, float]]:
        """
        Predicts the identity of faces in an input image by comparing their embeddings
        to known embeddings using Euclidean distance.

        Args:
            image (np.ndarray): Input RGB image containing faces.
            threshold (float, optional): Maximum Euclidean distance for a positive match.
                                        Lower values indicate stricter matching. Defaults to 0.6.

        Returns:
            List[Tuple[str, float]]: List of tuples containing the predicted identity and Euclidean distance
                                     for each detected face.

        Raises:
            RuntimeError: If the model is not loaded, no known embeddings are available, or prediction fails.
        """
        if not self.embedding_extractor.model:
            raise RuntimeError("Model is not loaded. Call load_model() first.")
        if not self.known_embeddings:
            raise RuntimeError("No known embeddings loaded. Call load_known_embeddings() first.")

        try:
            embeddings = self.embedding_extractor.extract_embeddings_from_image_with_uid(image)
            results = []
            for index, det, embedding in embeddings:
                best_match = ("Unknown", float('inf'))
                for label, known_embs in self.known_embeddings.items():
                    for known_emb in known_embs:
                        dist = self.euclidean_distance(embedding, known_emb)
                        if dist < best_match[1] and dist <= threshold:
                            best_match = (label, dist)
                results.append({"id":best_match[0], "dist": best_match[1],"face":det})
            return results
        except Exception as e:
            raise RuntimeError(f"Failed to predict face identity: {e}") from e

    def predict_from_video(self, video_path: str, threshold: float = 0.6, frame_skip: int = 5,
                           max_frames: Optional[int] = None) -> List[Tuple[str, float]]:
        """
        Predicts face identities from a video by processing frames and comparing embeddings
        using Euclidean distance.

        Args:
            video_path (str): Path to the video file.
            threshold (float, optional): Maximum Euclidean distance for a positive match.
                                        Lower values indicate stricter matching. Defaults to 0.6.
            frame_skip (int, optional): Number of frames to skip between processing. Defaults to 5.
            max_frames (Optional[int], optional): Maximum number of frames to process. Defaults to None.

        Returns:
            List[Tuple[str, float]]: List of tuples containing the predicted identity and Euclidean distance
                                     for each detected face across processed frames.

        Raises:
            FileNotFoundError: If the video file does not exist.
            RuntimeError: If the model is not loaded, no known embeddings are available, or prediction fails.
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        if not self.embedding_extractor.model:
            raise RuntimeError("Model is not loaded. Call load_model() first.")
        if not self.known_embeddings:
            raise RuntimeError("No known embeddings loaded. Call load_known_embeddings() first.")

        try:
            embeddings = self.embedding_extractor.extract_embeddings_from_video(
                video_path, frame_skip, max_frames
            )
            results = []

            for embedding in embeddings:
                best_match = ("Unknown", float('inf'))
                for person, known_embs in self.known_embeddings.items():
                    for known_emb in known_embs:
                        dist = self.euclidean_distance(embedding, known_emb)
                        if dist < best_match[1] and dist <= threshold:
                            best_match = (person, dist)
                results.append(best_match)

            return results
        except Exception as e:
            raise RuntimeError(f"Failed to predict face identity from video: {e}") from e
