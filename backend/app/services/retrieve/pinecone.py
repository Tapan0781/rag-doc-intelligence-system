from __future__ import annotations

from ..embed.fastembed import embed_texts
from ...clients.pinecone import get_index
from ...core.config import Chunk, settings


def upsert_chunks(chunks: list[Chunk], embeddings: list[list[float]]) -> None:
    index = get_index()
    vectors = [
        (
            chunk.id,
            embeddings[i],
            {"text": chunk.text, **chunk.metadata},
        )
        for i, chunk in enumerate(chunks)
    ]
    index.upsert(vectors=vectors)


def query_similar(text: str, top_k: int | None = None) -> list[dict]:
    index = get_index()
    top_k = top_k or settings.max_query_results
    vector = embed_texts([text])[0]
    results = index.query(vector=vector, top_k=top_k, include_metadata=True)
    matches = results.get("matches", [])
    return [
        {
            "id": m.get("id"),
            **(m.get("metadata") or {}),
        }
        for m in matches
        if "metadata" in m
    ]
