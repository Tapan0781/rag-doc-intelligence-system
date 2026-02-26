from __future__ import annotations

from pinecone import Pinecone

from ..core.config import settings


_pc = Pinecone(api_key=settings.pinecone_api_key)


def get_index():
    if not settings.pinecone_host:
        return _pc.Index(settings.pinecone_index_name)
    return _pc.Index(host=settings.pinecone_host)
