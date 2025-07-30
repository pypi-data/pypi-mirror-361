import numpy as np


class Utils:
    @classmethod
    def crop_from_image(cls, image: np.ndarray, box, margin: int = 10) -> np.ndarray:
        """Crop image according to given bounding box"""
        x, y, w, h = box
        h_img, w_img = image.shape[:2]
        x1 = max(x - margin, 0)
        y1 = max(y - margin, 0)
        x2 = min(x + w + margin, w_img)
        y2 = min(y + h + margin, h_img)
        return image[y1:y2, x1:x2]