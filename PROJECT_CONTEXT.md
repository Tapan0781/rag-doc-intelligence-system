# Project Context — rag-doc-intelligence-system

## 🎯 Goal
Build a production-style Retrieval-Augmented Generation (RAG) system:

- PDF ingestion
- Chunking
- Embedding via FastEmbed (bge-small-en-v1.5 ONNX)
- Vector storage in Pinecone
- Retrieval (top-k)
- LLM answer generation (migrating away from OpenAI due to quota issues)
- FastAPI backend
- Streamlit frontend
- Redis metadata store
- Codex CLI used for development

---

## 🏗 Architecture Overview

User → FastAPI → 
1) Embed via FastEmbed
2) Store vectors in Pinecone
3) Store document metadata in Redis
4) Query → Retrieve chunks
5) Generate answer via LLM
6) Return response

---

## 📁 Important Files

backend/app/main.py  
backend/app/api/v1/routes/ingest.py  
backend/app/api/v1/routes/query.py  
backend/app/services/embed/fastembed.py  
backend/app/services/retrieve/pinecone.py  
backend/app/services/rag/pipeline.py  
backend/app/services/llm/ (LLM provider lives here)  
frontend/streamlit_app.py  

---

## ⚙ Current Embedding Setup

Model:
- BAAI/bge-small-en-v1.5 (via FastEmbed ONNX)

Embedding dimension:
- 384

Pinecone index MUST:
- dimension = 384
- metric = cosine

Important fix already needed:
- Convert embeddings from float32 → Python float before upsert.

Correct pattern:

```python
values = [float(x) for x in embeddings[i]]