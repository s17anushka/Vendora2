"""
Pydantic schemas for the Sentiment Analysis API.
"""

from pydantic import BaseModel, Field


# ─────────────────────────────────────────
# REQUEST SCHEMAS
# ─────────────────────────────────────────
class SentimentRequest(BaseModel):
    text: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="The review text to analyze",
        json_schema_extra={"example": "The plumber was very professional and on time"},
    )


class BatchSentimentRequest(BaseModel):
    texts: list[str] = Field(
        ...,
        min_length=1,
        max_length=50,
        description="List of review texts to analyze (max 50)",
        json_schema_extra={
            "example": [
                "Great experience with the electrician",
                "Very bad service, came late",
                "It was okay, nothing special",
            ]
        },
    )


# ─────────────────────────────────────────
# RESPONSE SCHEMAS
# ─────────────────────────────────────────
class SentimentResponse(BaseModel):
    text: str = Field(description="Original input text")
    sentiment: str = Field(description="Predicted sentiment: positive, neutral, or negative")
    confidence: float = Field(description="Model confidence score (0-1)")
    raw_label: str = Field(description="Raw model output label")


class BatchSentimentResponse(BaseModel):
    results: list[SentimentResponse]
    total: int = Field(description="Total number of predictions")


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    model_name: str
    labels: list[str]
