# rag-doc-intelligence-system

Minimal, production-ready RAG backend using FastAPI, FastEmbed, Pinecone, and Redis.

## End-to-end runbook

### 1) Prerequisites
- Python 3.12
- Redis running locally or accessible via `REDIS_URL`
- A Pinecone index created and ready
- OpenAI API key for answering

### 2) Environment variables
Create `.env` from `.env.example` and fill values:
- `PINECONE_API_KEY`
- `PINECONE_INDEX_NAME`
- `PINECONE_HOST` (optional if using index name only)
- `OPENAI_API_KEY`

### 3) Install dependencies
```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

### 4) Run backend (FastAPI)
```bash
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5) Run frontend (Streamlit)
In a new terminal:
```bash
export API_URL=http://localhost:8000/api/v1
streamlit run frontend/streamlit_app.py
```

### 6) Ingest a PDF
Use the Streamlit UI, or curl:
```bash
curl -F "file=@/path/to/document.pdf" http://localhost:8000/api/v1/ingest
```

### 7) Ask a question
```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is this document about?"}'
```

### 8) Run tests
```bash
pytest
```

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
