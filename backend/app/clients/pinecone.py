from __future__ import annotations

from pinecone import Pinecone

from ..core.config import settings
from ..core.errors import AppError


def _client() -> Pinecone:
    if not settings.pinecone_api_key:
        raise AppError("PINECONE_API_KEY is not set.", status_code=500, error_code="config_error")
    return Pinecone(api_key=settings.pinecone_api_key)


def get_index():
    if not settings.pinecone_index_name and not settings.pinecone_host:
        raise AppError(
            "PINECONE_INDEX_NAME or PINECONE_HOST is not set.",
            status_code=500,
            error_code="config_error",
        )
    pc = _client()
    if not settings.pinecone_host:
        return pc.Index(settings.pinecone_index_name)
    return pc.Index(host=settings.pinecone_host)
