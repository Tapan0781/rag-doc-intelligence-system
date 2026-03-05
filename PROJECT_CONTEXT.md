codex <<'PROMPT'
You are working in the repository "rag-doc-intelligence-system".

First understand the project before making any changes.

STEP 1 — Read project context
Open and carefully read the following files to understand the architecture:

- PROJECT_CONTEXT.md
- README.md
- pyproject.toml
- backend/app/main.py
- backend/app/api/v1/routes/query.py
- backend/app/services/rag/pipeline.py
- backend/app/services/llm/openai_chat.py
- backend/app/utils/text.py

Summarize the system architecture in 5–8 bullet points before proceeding.

------------------------------------------------

STEP 2 — Implement Phase 1 improvements

Goal: Improve retrieval quality and prevent hallucinated answers.

Implement the following upgrades:

1) Retrieval Improvements
- Keep Pinecone dense retrieval.
- Retrieve TOP_K_DENSE = 20 chunks.
- Implement a reranking step using a cross-encoder reranker:
  Model: BAAI/bge-reranker-base

Pipeline should be:

Query
→ embed query
→ Pinecone search (top 20)
→ rerank chunks
→ select top 6 chunks
→ send to LLM

------------------------------------------------

2) Strict grounded answering

Modify the LLM prompt so the model:

- MUST answer using provided context only
- MUST NOT fabricate information
- MUST respond:

"Not found in the provided document."

if the answer is not present in the retrieved chunks.

------------------------------------------------

3) Answer cleaning

Improve text cleaning utilities:

File:
backend/app/utils/text.py

Ensure final answers:

- remove trailing chunk ids
- remove bracket artifacts
- remove stray metadata
- keep the answer clean

------------------------------------------------

4) Config additions

Add configuration parameters in:

backend/app/core/config.py

RERANK_ENABLED = true
TOP_K_DENSE = 20
TOP_K_FINAL = 6
MIN_RETRIEVAL_SCORE = reasonable default

Ensure these values are configurable via environment variables.

------------------------------------------------

5) Maintain compatibility

Important constraints:

- Do NOT break Streamlit Cloud deployment
- Do NOT require Redis
- Keep API response format unchanged:

{
  "answer": "...",
  "sources": [...],
  "source_ids": [...]
}

------------------------------------------------

STEP 3 — Testing

Update or add tests:

backend/tests/api/test_query_response.py
backend/tests/services/test_text_utils.py

Ensure:

- answers never contain chunk ids
- answers follow the response schema
- low retrieval score returns "Not found in the provided document."

------------------------------------------------

STEP 4 — Final checks

Before finishing:

Run tests:
pytest -q

Show a summary of files changed and explain the improvements.

Commit message:

"Phase 1: reranking retrieval pipeline, grounded answers, text cleaning improvements"

PROMPT