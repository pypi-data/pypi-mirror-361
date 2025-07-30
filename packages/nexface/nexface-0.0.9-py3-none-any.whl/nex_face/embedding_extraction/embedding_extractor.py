import os
import uuid
from importlib.resources import files
from keras.models import load_model
import numpy as np
import cv2
from typing import Iterator, Tuple, Optional, List, Dict

from nex_face.embedding_extraction.base_embedding_extractor import BaseEmbeddingExtraction
from nex_face.face_extraction.face_extractor import FaceDetection
from nex_face.models.face_detection_result_model import FaceDetectionResult
from nex_face.utils.utils import Utils


class EmbeddingExtraction(BaseEmbeddingExtraction):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(EmbeddingExtraction, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "_initialized"):
            self.model = None
            self.face_detector = FaceDetection()
            self._initialized = True

    def load_model(self, compile_model: bool = False):
        """
        Load the FaceNet model from embedded resources.
        """
        try:
            model_path = str(files("nex_face.resources").joinpath("facenet_keras_2024.h5"))
            self.model = load_model(model_path, compile=compile_model)
        except Exception as e:
            raise RuntimeError(f"Failed to load model: {e}") from e

    @classmethod
    def preprocess_face(cls, face: np.ndarray) -> np.ndarray:
        """
        Resize and normalize the face image for FaceNet model.

        Args:
            face (np.ndarray): Input face image.

        Returns:
            np.ndarray: Preprocessed face image.
        """
        face = cv2.resize(face, (160, 160))
        face = face.astype('float32') / 255.0
        mean, std = face.mean(), face.std()
        face = (face - mean) / std
        return np.expand_dims(face, axis=0)

    def extract_embedding(self, face_image: np.ndarray) -> np.ndarray:
        """
        Generate embedding from a face image.

        Args:
            face_image (np.ndarray): Raw face image.

        Returns:
            np.ndarray: Embedding vector.
        """
        try:
            preprocessed = self.preprocess_face(face_image)
            embedding = self.model.predict(preprocessed)
            return embedding[0]
        except Exception as e:
            raise RuntimeError(f"Failed to extract embedding: {e}") from e

    def extract_embeddings_from_image_with_uid(self, image: np.ndarray) -> List[Tuple[str, FaceDetectionResult, np.ndarray]]:
        """
        Detects all faces in the given image and extracts their corresponding embeddings.

        Args:
            image (np.ndarray): An RGB image represented as a NumPy array.

        Returns:
            List[Tuple[str, FaceDetectionResult, np.ndarray]]: A list containing a single tuple. The first element
                                          is the provided file_name or a generated UUID string,
                                          and the second element is a list of extracted face embeddings
                                          (one for each detected face).

        Raises:
            RuntimeError: If face detection or embedding extraction fails for any reason.
        """
        try:
            detections = self.face_detector.predict(image)
            embeddings = []
            for det in detections:
                index =  str(uuid.uuid4())
                x, y, w, h = int(det.x1), int(det.y1), int(det.w), int(det.h)
                face = Utils.crop_from_image(image, box=(x, y, w, h))
                if face.size == 0:
                    continue
                embedding = self.extract_embedding(face)
                embeddings.append((index, det, embedding))
            return embeddings
        except Exception as e:
            raise RuntimeError(f"Failed to extract embeddings from image: {e}") from e

    def extract_embeddings_from_image(self, image: np.ndarray) -> List[np.ndarray]:
        """
        Detects all faces in the given image and extracts their corresponding embeddings.

        Args:
            image (np.ndarray): An RGB image represented as a NumPy array.

        Returns:
            List[np.ndarray]: A list of face embeddings, one for each detected face in the image.

        Raises:
            RuntimeError: If face detection or embedding extraction fails for any reason.
        """
        try:
            detections = self.face_detector.predict(image)
            embeddings = []
            for det in detections:
                x, y, w, h = int(det.x1), int(det.y1), int(det.w), int(det.h)
                face = Utils.crop_from_image(image, box=(x, y, w, h))
                if face.size == 0:
                    continue
                embedding = self.extract_embedding(face)
                embeddings.append(embedding)
            return embeddings
        except Exception as e:
            raise RuntimeError(f"Failed to extract embeddings from image: {e}") from e

    def extract_embeddings_from_folder(self, folder_path: str) -> Dict[str, List[Tuple[str, np.ndarray]]]:
        """
        Extract embeddings from all images in all subfolders.

        Each subfolder is treated as a person/class label.

        Args:
            folder_path (str): Path to root folder.

        Returns:
            Dict[str, List[Tuple[str, np.ndarray]]]: Dictionary of embeddings per person, with filenames.
        """

        embeddings_dict = {}

        try:
            for subfolder_name in os.listdir(folder_path):
                subfolder_path = os.path.join(folder_path, subfolder_name)
                if not os.path.isdir(subfolder_path):
                    continue

                embeddings = []
                for file_name in os.listdir(subfolder_path):
                    if file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
                        file_path = os.path.join(subfolder_path, file_name)
                        image = cv2.imread(file_path)
                        if image is None:
                            continue
                        face_embeddings = self.extract_embeddings_from_image(image)

                        for emb in face_embeddings:
                            embeddings.append((file_name, emb))

                if embeddings:
                    embeddings_dict[subfolder_name] = embeddings

            return embeddings_dict

        except Exception as e:
            raise RuntimeError(f"Failed to extract embeddings from folder: {e}") from e

    def extract_embeddings_from_video(self, video_path: str,
                                      frame_skip: int = 5,
                                      max_frames: Optional[int] = None) -> Iterator[Tuple[str, Optional[List[np.ndarray]]]]:
        """
        Extract face embeddings from frames in a video file, yielding progress updates.

        Args:
            video_path (str): Path to the video file.
            frame_skip (int): Number of frames to skip between processing.
            max_frames (Optional[int]): Max number of frames to process.

        Yields:
            Tuple[str, Optional[List[np.ndarray]]]: A tuple containing a status message and,
            when complete, the list of face embeddings from video frames.

        Raises:
            FileNotFoundError: If the video file does not exist.
            IOError: If the video cannot be opened.
            RuntimeError: If an error occurs during processing.
        """

        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")

        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise IOError(f"Cannot open video: {video_path}")

            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            embeddings = []
            frame_count = 0
            processed_frames = 0

            yield f"Started processing video: {video_path}, total frames: {total_frames}", None

            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                if frame_count % frame_skip == 0:
                    frame_embeddings = self.extract_embeddings_from_image(frame)
                    embeddings.extend(frame_embeddings)
                    processed_frames += 1

                    progress_percent = (frame_count / total_frames * 100) if total_frames > 0 else 0
                    yield f"Processed {processed_frames} frames ({progress_percent:.1f}% complete)", None

                    if max_frames is not None and processed_frames >= max_frames:
                        break

                frame_count += 1

            cap.release()
            yield f"Completed processing {processed_frames} frames", embeddings

        except Exception as e:
            raise RuntimeError(f"Failed to extract embeddings from video: {e}") from e
