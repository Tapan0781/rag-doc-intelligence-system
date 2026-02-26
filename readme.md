# rag-doc-intelligence-system

Minimal, production-ready RAG backend using FastAPI, FastEmbed, Pinecone, and Redis.

## Setup

1. Create `.env` from `.env.example` and set keys.
2. Install deps from `pyproject.toml`.

## Run API

```bash
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

## Run Frontend

```bash
streamlit run frontend/streamlit_app.py
```
