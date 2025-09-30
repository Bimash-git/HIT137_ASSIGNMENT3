from __future__ import annotations
from PIL import Image
import numpy as np
try:
    import cv2  # type: ignore
    _HAS_CV2 = True
except Exception:
    _HAS_CV2 = False

def load_image(path: str) -> Image.Image:
    if _HAS_CV2:
        im = cv2.imread(path, cv2.IMREAD_COLOR)
        if im is None:
            raise ValueError(f"Could not open image: {path}")
        im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
        return Image.fromarray(im)
    return Image.open(path).convert("RGB")

def preprocess_image_cv2(pil_img: Image.Image, size=(224,224), blur=False, edges=False, gray=False) -> Image.Image:
    if not _HAS_CV2:
        return pil_img.resize(size)
    im = np.array(pil_img)
    import cv2
    im = cv2.resize(im, size, interpolation=cv2.INTER_AREA)
    if gray:
        im = cv2.cvtColor(im, cv2.COLOR_RGB2GRAY)
        im = cv2.cvtColor(im, cv2.COLOR_GRAY2RGB)
    if blur:
        im = cv2.GaussianBlur(im, (3,3), 0)
    if edges:
        e = cv2.Canny(im, 100, 200)
        im = cv2.cvtColor(e, cv2.COLOR_GRAY2RGB)
    return Image.fromarray(im)
