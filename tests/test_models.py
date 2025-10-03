from __future__ import annotations
from PIL import Image
from tk_ai_gui.controller import ModelManager

def test_text_sentiment_shape_and_keys():
    mm = ModelManager()
    out = mm.run("sentiment", "This subject is great!")
    assert isinstance(out, list) and len(out) >= 1
    assert {"label","score"}.issubset(out[0].keys())
    assert isinstance(out[0]["label"], str)
    assert 0.0 <= float(out[0]["score"]) <= 1.0

def test_image_classifier_shape_and_keys():
    mm = ModelManager()
    img = Image.new('RGB', (224, 224), (0, 0, 0))
    out = mm.run("image", img)
    assert isinstance(out, list) and len(out) >= 1
    assert {"label","score"}.issubset(out[0].keys())

def test_offline_fallback_survives():
    mm = ModelManager()
    out1 = mm.run("sentiment", "bad")
    out2 = mm.run("image", Image.new("RGB",(32,32)))
    assert isinstance(out1, list) and isinstance(out2, list)
    assert {"label","score"}.issubset(out1[0].keys())
    assert {"label","score"}.issubset(out2[0].keys())
