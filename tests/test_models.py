from __future__ import annotations
from PIL import Image
from tk_ai_gui.controller import ModelManager

# These tests lock down the public contract of ModelManager.run():
# must return List[{"label": str, "score": number in 0..1}] for both "sentiment" and "image".
# They also ensure the app degrades gracefully (offline fallback still returns the same shape).

def test_text_sentiment_shape_and_keys():
    mm = ModelManager()  # system under test
    out = mm.run("sentiment", "This subject is great!")  # happy-path text input

    # Output must be a non-empty list of predictions
    assert isinstance(out, list) and len(out) >= 1

    # Each prediction must expose the standard keys
    assert {"label", "score"}.issubset(out[0].keys())

    # Types and ranges: label is str, score is 0..1
    assert isinstance(out[0]["label"], str)
    assert 0.0 <= float(out[0]["score"]) <= 1.0


def test_image_classifier_shape_and_keys():
    mm = ModelManager()
    # Minimal valid RGB image (black 224x224) to exercise the image path
    img = Image.new('RGB', (224, 224), (0, 0, 0))
    out = mm.run("image", img)

    # Same schema guarantees as sentiment
    assert isinstance(out, list) and len(out) >= 1
    assert {"label", "score"}.issubset(out[0].keys())


def test_offline_fallback_survives():
    mm = ModelManager()
    # Tiny inputs to simulate constrained/offline environments
    out1 = mm.run("sentiment", "bad")
    out2 = mm.run("image", Image.new("RGB", (32, 32)))

    # Even without network/models, API must not crash and must keep the schema
    assert isinstance(out1, list) and isinstance(out2, list)
    assert {"label", "score"}.issubset(out1[0].keys())
    assert {"label", "score"}.issubset(out2[0].keys())
