from __future__ import annotations
from transformers import pipeline
from PIL import Image
from .base import AIModelBase
from ..mixins import SaveLoadMixin
from ..utils.decorators import log_call, time_call


def _device():
    try:
        import torch
        # If GPU is available, return device 0, else use CPU (-1)
        return 0 if torch.cuda.is_available() else -1
    except Exception:
        # If torch not installed or error occurs, default to CPU
        return -1


class ImageClassifierModel(SaveLoadMixin, AIModelBase):
    def __init__(self, model_id: str = 'google/vit-base-patch16-224') -> None:
        """
        model_id: pretrained model identifier from Hugging Face hub
        """
        # Initialize base AI model with given model_id and task type
        super().__init__(model_id=model_id, task='image-classification')

        # Create Hugging Face pipeline for image classification
        self._set_pipeline(
            pipeline('image-classification', model=model_id, device=_device())
        )

    @log_call
    @time_call
    def run(self, input_data: Image.Image | str):

         # Runs the image classification model on input image.

        # input_data: can be a PIL image or a file path
        # returns: top-k predicted labels with confidence scores

        return self._get_pipeline()(input_data)

    def info(self) -> str:
        
        # Returns description of model usage and expected input/output format

        return super().info() + "\nCategory: Vision | Input: RGB image | Output: top-k labels+scores"
