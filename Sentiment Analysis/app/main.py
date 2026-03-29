"""
FastAPI Application — Sentiment Analysis API
Serves the fine-tuned DistilBERT sentiment model via REST endpoints.
Designed for deployment on Hugging Face Spaces (Docker SDK).
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import time

from app.model import get_classifier, predict_sentiment, predict_batch, LABEL_MAP
from app.schemas import (
    SentimentRequest,
    BatchSentimentRequest,
    SentimentResponse,
    BatchSentimentResponse,
    HealthResponse,
)


# ─────────────────────────────────────────
# LIFESPAN — load model on startup
# ─────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Pre-load the model at startup for fast first requests."""
    get_classifier()
    yield


# ─────────────────────────────────────────
# APP INSTANCE
# ─────────────────────────────────────────
app = FastAPI(
    title="🎯 Sentiment Analysis API",
    description=(
        "A production-ready REST API for **service review sentiment analysis** "
        "powered by a fine-tuned **DistilBERT** model.\n\n"
        "### Supported Labels\n"
        "| Label | Description |\n"
        "|-------|-------------|\n"
        "| `positive` | The review expresses satisfaction |\n"
        "| `neutral` | The review is ambiguous or mixed |\n"
        "| `negative` | The review expresses dissatisfaction |\n\n"
        "### Features\n"
        "- Single & batch prediction endpoints\n"
        "- Smart post-processing with keyword & confidence rules\n"
        "- Beautiful interactive web UI at `/`\n"
        "- Deployed on Hugging Face Spaces\n"
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS — allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for the web UI
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
if os.path.isdir(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


# ─────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────

@app.get("/", include_in_schema=False)
async def serve_ui():
    """Serve the interactive web UI."""
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Sentiment Analysis API is running. Visit /docs for API documentation."}


@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """Check if the API and model are operational."""
    try:
        classifier = get_classifier()
        return HealthResponse(
            status="healthy",
            model_loaded=classifier is not None,
            model_name="distilbert-base-uncased (fine-tuned)",
            labels=list(LABEL_MAP.values()),
        )
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Model not available: {str(e)}")


@app.post("/predict", response_model=SentimentResponse, tags=["Prediction"])
async def predict(request: SentimentRequest):
    """
    Analyze the sentiment of a single review text.

    Returns the predicted sentiment label (positive, neutral, or negative).
    """
    try:
        result = predict_sentiment(request.text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@app.post("/predict/batch", response_model=BatchSentimentResponse, tags=["Prediction"])
async def predict_batch_endpoint(request: BatchSentimentRequest):
    """
    Analyze the sentiment of multiple review texts in one request (max 50).

    Returns a list of sentiment predictions with overall count.
    """
    try:
        results = predict_batch(request.texts)
        return BatchSentimentResponse(results=results, total=len(results))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch prediction failed: {str(e)}")
