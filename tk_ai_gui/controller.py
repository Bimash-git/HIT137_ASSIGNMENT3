from __future__ import annotations
from .models.text_sentiment import TextSentimentModel
from .models.image_classifier import ImageClassifierModel

# This is just a simple rule-based fallback for sentiment
# If the actual ML model isn't available, we'll use this
class _RuleSentimentFallback:
    def info(self) -> str: 
        return "Fallback Sentiment (rule-based)"

    def run(self, text: str):
        # In tis line we convert text to lowercase so we can match keywords easily
        t = (text or "").lower()

        # Here we Check if the text contains any "positive" words
        pos = any(w in t for w in ["good","great","love","awesome","fantastic","happy"])

        # If we find one, label it as POSITIVE, otherwise NEGATIVE
        lab = "POSITIVE" if pos else "NEGATIVE"

        # Just return a hardcoded confidence score for now
        return [{"label": lab, "score": 0.75}]


# Same idea here but for images, 
# if the real image model isn’t available we just return a dummy label
class _RuleImageFallback:
    def info(self) -> str: 
        return "Fallback Image Classifier (constant)"

    def run(self, _img): 
        return [{"label":"object","score":0.50}]


class ModelManager:
    def __init__(self) -> None:
        try:
            # Here we try loading the actual ML models first
            self._models = {
                "sentiment": TextSentimentModel(), 
                "image": ImageClassifierModel()
            }

            # Quick test run to make sure the sentiment model works
            _ = self._models["sentiment"].run("ok")

        except Exception:
            # If something fails (like models not being available),
            # fall back to the simple rule-based versions
            self._models = {
                "sentiment": _RuleSentimentFallback(), 
                "image": _RuleImageFallback()
            }

    # Get the model by its key ("sentiment" or "image")
    def get(self, key: str): 
        return self._models[key]

    # Run the model on given input data
    def run(self, key: str, input_data): 
        return self._models[key].run(input_data)
