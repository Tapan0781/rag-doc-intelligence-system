from __future__ import annotations

from ..embed.fastembed import embed_texts
from ...clients.pinecone import get_index
from ...core.config import Chunk, settings


def _to_float_list(vec) -> list[float]:
    # Handles numpy float32 / lists etc (prevents Pinecone float32 type error)
    return [float(x) for x in vec]


def upsert_chunks(chunks: list[Chunk], embeddings) -> None:
    index = get_index()
    vectors = []
    for i, chunk in enumerate(chunks):
        vectors.append(
            (
                chunk.id,
                _to_float_list(embeddings[i]),
                {"text": chunk.text, **chunk.metadata},
            )
        )
    index.upsert(vectors=vectors)


def query_similar(text: str, top_k: int | None = None) -> list[dict]:
    index = get_index()
    top_k = top_k or settings.max_query_results
    vector = _to_float_list(embed_texts([text])[0])

    results = index.query(
        vector=vector,
        top_k=top_k,
        include_metadata=True,
    )

    matches = results.get("matches", []) or []
    out: list[dict] = []

    for m in matches:
        md = m.get("metadata") or {}
        out.append(
            {
                "id": m.get("id"),
                "score": float(m.get("score", 0.0) or 0.0),
                "text": md.get("text", ""),
                "document_id": md.get("document_id"),
                "chunk_id": md.get("chunk_id") or md.get("chunk_index"),
                "filename": md.get("filename") or md.get("source") or "unknown",
                "page": md.get("page"),
                "chunk_index": md.get("chunk_index"),
            }
        )

    return out
