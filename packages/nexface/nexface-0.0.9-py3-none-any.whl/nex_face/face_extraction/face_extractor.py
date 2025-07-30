from typing import List

import cv2
import onnx
import numpy as np
from nex_face.models.face_detection_result_model import FaceDetectionResult
from importlib.resources import files

"""
FaceDetection class implements a singleton pattern for face detection using OpenCV's YuNet model.
It loads an ONNX-based face detection model, processes input images, and returns detected face landmarks
with confidence scores.

Attributes:
    _instance (FaceDetection): Singleton instance of the class.
    _initialized (bool): Flag to prevent re-initialization.
    model (cv2.FaceDetectorYN): OpenCV face detection model instance.
"""

class FaceDetection:
    _instance = None

    def __new__(cls, *args, **kwargs):
        """
        Ensures a single instance of FaceDetection is created (Singleton pattern).

        Returns:
            FaceDetection: The singleton instance.
        """
        if cls._instance is None:
            cls._instance = super(FaceDetection, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """
        Initializes the FaceDetection instance if not already initialized.
        Sets the model to None and marks the instance as initialized.
        """
        if not hasattr(self, "_initialized"):
            self.model = None
            self._initialized = True

    def update_model(self, data, label):
        """
        Placeholder method for updating the face detection model. Not implemented.

        Args:
            data: Input data for model update.
            label: Labels corresponding to the input data.

        Raises:
            NotImplementedError: Always raised as this method is not implemented.
        """
        raise NotImplementedError("update_model() is not implemented for FaceDetection.")

    def load_model(
        self,
        width: int,
        height: int,
        score_threshold: float = 0.75,
        nms_threshold: float = 0.3,
        top_k: int = 5000
    ):
        """
        Loads the YuNet face detection model from an ONNX file.

        Args:
            width (int): Input image width for the model.
            height (int): Input image height for the model.
            score_threshold (float, optional): Confidence threshold for detections. Defaults to 0.75.
            nms_threshold (float, optional): Non-maximum suppression threshold. Defaults to 0.3.
            top_k (int, optional): Maximum number of detections to keep before NMS. Defaults to 5000.

        Raises:
            ValueError: If the model file is not in ONNX format or is invalid.
            FileNotFoundError: If the model file is not found.
            RuntimeError: If the model fails to load.
        """
        model_path = str(files("nex_face.resources").joinpath("face_detection_yunet_2023mar.onnx"))
        try:
            if not model_path.lower().endswith(".onnx"):
                raise ValueError(f"Model file must be ONNX format: {model_path}")

            self.model = cv2.FaceDetectorYN.create(
                model_path,
                "",
                (width, height),
                score_threshold,
                nms_threshold,
                top_k
            )

            if self.model is None:
                raise RuntimeError("cv2.FaceDetectorYN.create() returned None")

        except FileNotFoundError:
            raise FileNotFoundError(f"Model file not found: {model_path}")
        except onnx.onnx_cpp2py_export.checker.ValidationError as e:
            raise ValueError(f"Invalid ONNX model file: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to load face detection model: {e}")

    def predict(self, data: np.ndarray) -> List[FaceDetectionResult]:
        """
        Performs face detection on the input image and returns detected faces with landmarks.

        Args:
            data (np.ndarray): Input image as a 3-channel (RGB) NumPy array.

        Returns:
            List[FaceDetectionResult]: List of detected faces, each containing bounding box coordinates,
                                      facial landmarks (eyes, nose, mouth), and confidence score.

        Raises:
            RuntimeError: If the model is not loaded or detection fails.
            TypeError: If the input is not a NumPy array.
            ValueError: If the input image is not a 3-channel RGB image.
        """
        try:
            if self.model is None:
                raise RuntimeError("Model is not loaded. Call load_model() before prediction.")

            if not isinstance(data, np.ndarray):
                raise TypeError("Input data must be a NumPy ndarray.")

            if data.ndim != 3 or data.shape[2] != 3:
                raise ValueError("Input image must be a 3-channel (RGB) image.")

            self.model.setInputSize((data.shape[1], data.shape[0]))

            result = []
            success, faces = self.model.detect(data)
            if not success:
                raise RuntimeError("Model detection failed.")

            if faces is not None:
                for face in faces:
                    (
                        x1, y1, w, h,
                        x_right_eye, y_right_eye,
                        x_left_eye, y_left_eye,
                        x_nose_tip, y_nose_tip,
                        x_right_corner_mouth, y_right_corner_mouth,
                        x_left_corner_mouth, y_left_corner_mouth,
                        confidence
                    ) = face

                    result.append(FaceDetectionResult(
                        x1=x1, y1=y1, w=w, h=h,
                        x_right_eye=x_right_eye, y_right_eye=y_right_eye,
                        x_left_eye=x_left_eye, y_left_eye=y_left_eye,
                        x_nose_tip=x_nose_tip, y_nose_tip=y_nose_tip,
                        x_right_corner_mouth=x_right_corner_mouth, y_right_corner_mouth=y_right_corner_mouth,
                        x_left_corner_mouth=x_left_corner_mouth, y_left_corner_mouth=y_left_corner_mouth,
                        confidence=confidence
                    ))

            return result

        except Exception as e:
            raise RuntimeError(f"Face Detection Error in predict(): {e}")