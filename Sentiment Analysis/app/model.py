"""
Sentiment Analysis Model Loader & Predictor
Uses the fine-tuned DistilBERT model for 3-class sentiment classification.
"""

import os
from transformers import pipeline

# ─────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────
MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sentiment_model")

LABEL_MAP = {
    "LABEL_0": "negative",
    "LABEL_1": "neutral",
    "LABEL_2": "positive",
}

NEUTRAL_KEYWORDS = [
    "okay", "average", "fine", "not bad", "not good",
    "nothing special", "decent", "so so", "could be better",
    "mediocre", "alright",
]

CONFIDENCE_THRESHOLD = 0.85


# ─────────────────────────────────────────
# SINGLETON MODEL LOADER
# ─────────────────────────────────────────
_classifier = None


def get_classifier():
    """Load the model once and cache it globally."""
    global _classifier
    if _classifier is None:
        print(f"⏳ Loading model from {MODEL_DIR} ...")
        _classifier = pipeline("text-classification", model=MODEL_DIR)
        print("✅ Model loaded successfully!")
    return _classifier


# ─────────────────────────────────────────
# PREDICTION LOGIC
# ─────────────────────────────────────────
def predict_sentiment(text: str) -> dict:
    """
    Run sentiment prediction with smart post-processing rules.

    Returns a dict with:
        - text: the original input
        - sentiment: "positive" | "neutral" | "negative"
        - confidence: float 0-1
        - raw_label: the raw model output label
    """
    classifier = get_classifier()
    result = classifier(text)[0]

    raw_label = result["label"]
    confidence = round(result["score"], 4)
    sentiment = LABEL_MAP.get(raw_label, raw_label)

    text_lower = text.lower()

    # Rule 1: keyword-based neutral override
    if any(keyword in text_lower for keyword in NEUTRAL_KEYWORDS):
        sentiment = "neutral"

    # Rule 2: low confidence → neutral fallback
    elif confidence < CONFIDENCE_THRESHOLD:
        sentiment = "neutral"

    return {
        "text": text,
        "sentiment": sentiment,
        "confidence": confidence,
        "raw_label": raw_label,
    }


def predict_batch(texts: list[str]) -> list[dict]:
    """Run sentiment prediction on a list of texts."""
    return [predict_sentiment(t) for t in texts]
