---
title: Sentiment Analysis API
emoji: 🎯
colorFrom: purple
colorTo: green
sdk: docker
app_port: 7860
pinned: false
license: mit
---

# 🎯 Sentiment Analysis API

A production-ready FastAPI application for **service review sentiment analysis** powered by a fine-tuned **DistilBERT** model.

## Model Details

- **Base Model**: `distilbert-base-uncased`
- **Task**: Sequence Classification (3 classes)
- **Labels**: `positive`, `neutral`, `negative`
- **Training Data**: Amazon service reviews + synthetic service review data

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Interactive Web UI |
| `GET` | `/health` | Health check |
| `GET` | `/docs` | Swagger API documentation |
| `POST` | `/predict` | Single text prediction |
| `POST` | `/predict/batch` | Batch prediction (up to 50 texts) |

## Quick Start (Local)

```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 7860 --reload
```

## Example API Usage

```python
import requests

response = requests.post(
    "http://localhost:7860/predict",
    json={"text": "The plumber was very professional and on time"}
)
print(response.json())
# {"text": "...", "sentiment": "positive", "confidence": 0.98, "raw_label": "LABEL_2"}
```

## Deploy to Hugging Face Spaces

1. Create a new Space on [Hugging Face](https://huggingface.co/new-space)
2. Select **Docker** as the SDK
3. Push this entire repository to the Space
4. The app will build and deploy automatically

## Tech Stack

- **FastAPI** — High-performance async API framework
- **Hugging Face Transformers** — DistilBERT model inference
- **PyTorch** — Deep learning backend
- **Pydantic** — Request/response validation
