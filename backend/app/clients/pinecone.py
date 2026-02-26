from __future__ import annotations

from pinecone import Pinecone

from ..core.config import settings


if not settings.pinecone_api_key:
    raise RuntimeError("PINECONE_API_KEY is not set.")

_pc = Pinecone(api_key=settings.pinecone_api_key)


def get_index():
    if not settings.pinecone_index_name and not settings.pinecone_host:
        raise RuntimeError("PINECONE_INDEX_NAME or PINECONE_HOST is not set.")
    if not settings.pinecone_host:
        return _pc.Index(settings.pinecone_index_name)
    return _pc.Index(host=settings.pinecone_host)
