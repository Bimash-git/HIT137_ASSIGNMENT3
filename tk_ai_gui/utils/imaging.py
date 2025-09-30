from __future__ import annotations
from PIL import Image
import numpy as np

#Implemented try except for optional cv2 import, if missing safe Pillow-only fallback.
try:
    import cv2  # type: ignore
    _HAS_CV2 = True # flag is used to know if the cv2 is available for rest of the code.
except Exception:
    _HAS_CV2 = False # take the pilloe path later.

def load_image(path: str) -> Image.Image:
    # Load an image from a file path, using cv2 if available for better compatibility.
    if _HAS_CV2:
        im = cv2.imread(path, cv2.IMREAD_COLOR) # Fast read via OpenCV (BGR order)
        if im is None: # used for bad path or unreadable file.
            raise ValueError(f"Could not open image: {path}")
        im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB) # Convert BGR ➜ RGB so colors are correct.
        return Image.fromarray(im) # Convert to PIL Image
    #Fallback: use Pillow and force RGB so downstream code is consistent.
    return Image.open(path).convert("RGB")

def preprocess_image_cv2(pil_img: Image.Image, size=(224,224), blur=False, edges=False, gray=False) -> Image.Image:

    """
    Resize and optionally apply grayscale, blur, or edge detection.
    Always returns a Pillow RGB image.
    """
    if not _HAS_CV2:
        return pil_img.resize(size)               # No cv2: do the minimum useful step (resize).

    im = np.array(pil_img)                        #  Pillow ➜ NumPy array (RGB) for OpenCV ops.

    import cv2                                    #  Local import keeps top-level optional.

    im = cv2.resize(im, size, interpolation=cv2.INTER_AREA)  # High-quality shrink for model inputs.

    if gray:
        im = cv2.cvtColor(im, cv2.COLOR_RGB2GRAY)            #  To 1-channel for true grayscale.
        im = cv2.cvtColor(im, cv2.COLOR_GRAY2RGB)            #  Back to 3-channel to keep shape consistent.

    if blur:
        im = cv2.GaussianBlur(im, (3, 3), 0)                  # Light denoise/smoothing.

    if edges:
        e = cv2.Canny(im, 100, 200)                           # Detect edges (single channel).
        im = cv2.cvtColor(e, cv2.COLOR_GRAY2RGB)              #  Back to RGB so callers don't break.

    return Image.fromarray(im)                                 #  Return Pillow Image for downstream use.
