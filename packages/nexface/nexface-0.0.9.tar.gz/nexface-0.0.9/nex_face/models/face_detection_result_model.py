from dataclasses import dataclass


@dataclass
class FaceDetectionResult:
    x1: int
    y1: int
    w: int
    h: int
    x_right_eye: float
    y_right_eye: float
    x_left_eye: float
    y_left_eye: float
    x_nose_tip: float
    y_nose_tip: float
    x_right_corner_mouth: float
    y_right_corner_mouth: float
    x_left_corner_mouth: float
    y_left_corner_mouth: float
    confidence: float
