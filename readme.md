# RAG Doc Intelligence System

Production‑style RAG pipeline with PDF ingestion, page‑level chunking, embeddings, vector retrieval, and a clean Streamlit UI.

## What This Project Does
- Ingests PDFs and chunks them by page.
- Embeds chunks using `BAAI/bge-small-en-v1.5`.
- Stores vectors in Pinecone and metadata in Redis.
- Retrieves top‑k relevant chunks and answers with an OpenAI model.
- UI supports per‑session API key, model selection, and ingest progress.

## Important Note About PDFs
PDFs are ignored in `.gitignore`. You must upload your own data to test ingestion and retrieval.

## Architecture (High Level)
1. **Ingest** → PDF → page text → chunks → embeddings → Pinecone + Redis
2. **Query** → embed question → Pinecone top‑k → LLM answer
3. **UI** → Streamlit app calling FastAPI

## Prerequisites
- Python 3.12
- Redis running locally or reachable via `REDIS_URL`
- Pinecone index created with:
  - dimension: `384`
  - metric: `cosine`
- OpenAI API key

## Environment Setup
Create `.env` from `.env.example` and fill values:
- `PINECONE_API_KEY`
- `PINECONE_INDEX_NAME` or `PINECONE_HOST`
- `OPENAI_API_KEY`

Optional tuning:
- `RAG_MIN_SCORE` (default `0.25`)
- `RAG_DEBUG` (default `false`)

## Install
```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

## Run Backend (FastAPI)
```bash
python -m uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

## Run Frontend (Streamlit)
```bash
export API_URL=http://localhost:8000/api/v1
streamlit run frontend/streamlit_app.py
```

## Ingest a PDF
Use the Streamlit UI (recommended). Or curl:
```bash
curl -F "file=@/path/to/your.pdf" http://localhost:8000/api/v1/ingest
```

## Ask a Question
```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is this document about?"}'
```

## Debug Retrieval
Set `RAG_DEBUG=true` in `.env` to include retrieval diagnostics in query responses:
- `top_k`
- `min_score`
- `matches` with `chunk_id`, `score`, and a short preview

## Testing
```bash
pytest
```

## UI Highlights
- Per‑session OpenAI API key input (not stored server‑side).
- Model selection and optional custom model entry.
- Async ingestion with progress bar.
- Clean answer view with sources hidden behind an expander.
