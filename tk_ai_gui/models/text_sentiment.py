from __future__ import annotations
from transformers import pipeline
from PIL import Image
from .base import AIModelBase
from ..mixins import SaveLoadMixin
from ..utils.decorators import log_call, time_call


def _device():
    try:
        import torch
        # If GPU is available, return device 0 (CUDA), else use CPU (-1)
        return 0 if torch.cuda.is_available() else -1
    except Exception:
        # If torch is not installed or fails, fallback to CPU
        return -1


class ImageClassifierModel(SaveLoadMixin, AIModelBase):
    def __init__(self, model_id: str = 'google/vit-base-patch16-224') -> None:
        """
        Initialize the image classification model.

        model_id: Hugging Face model identifier (default = ViT model)
        """
        # Call parent class initializer with model ID and task type
        super().__init__(model_id=model_id, task='image-classification')

        # Build Hugging Face pipeline for image classification
        # Uses GPU if available, otherwise CPU
        self._set_pipeline(
            pipeline('image-classification', model=model_id, device=_device())
        )

    @log_call   # Decorator: logs function call
    @time_call  # Decorator: measures runtime
    def run(self, input_data: Image.Image | str):
        """
        Run the image classification model.

        input_data: a PIL Image or a file path string
        returns: top-k predicted labels with confidence scores
        """
        # Pass input data to the pipeline and return predictions
        return self._get_pipeline()(input_data)

    def info(self) -> str:
        """
        Provide model description including category, input and output format.
        """
        return super().info() + "\nCategory: Vision | Input: RGB image | Output: top-k labels+scores"
