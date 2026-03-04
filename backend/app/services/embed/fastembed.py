from __future__ import annotations

from fastembed import TextEmbedding

from ...core.config import settings


def _embedder() -> TextEmbedding:
    return TextEmbedding(model_name=settings.embedding_model)


def embed_texts(texts: list[str]) -> list[list[float]]:
    model = _embedder()
    return [list(vec) for vec in model.embed(texts)]
