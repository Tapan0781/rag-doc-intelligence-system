from __future__ import annotations

import json
from datetime import datetime, timezone

from ...clients.redis import get_client


_DOC_STORE: dict[str, dict] = {}


def save_document_metadata(
    document_id: str,
    filename: str,
    checksum_sha256: str,
    page_count: int,
    chunk_count: int,
) -> None:
    payload = {
        "document_id": document_id,
        "filename": filename,
        "checksum_sha256": checksum_sha256,
        "page_count": page_count,
        "chunk_count": chunk_count,
        "status": "completed",
        "progress_current_chunks": chunk_count,
        "progress_total_chunks": chunk_count,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    key = f"rag:doc:{document_id}"
    client = get_client()
    if client:
        client.set(key, json.dumps(payload), ex=60 * 60 * 24 * 30)
    else:
        _DOC_STORE[key] = payload


def get_document_metadata(document_id: str) -> dict | None:
    key = f"rag:doc:{document_id}"
    client = get_client()
    if client:
        raw = client.get(key)
        if not raw:
            return None
        return json.loads(raw.decode("utf-8"))
    return _DOC_STORE.get(key)


def set_document_status(
    document_id: str,
    status: str,
    error: str | None = None,
    filename: str | None = None,
    progress_current_chunks: int | None = None,
    progress_total_chunks: int | None = None,
) -> None:
    key = f"rag:doc:{document_id}"
    payload = {
        "document_id": document_id,
        "status": status,
        "error": error,
        "filename": filename,
        "progress_current_chunks": progress_current_chunks,
        "progress_total_chunks": progress_total_chunks,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    client = get_client()
    if client:
        client.set(key, json.dumps(payload), ex=60 * 60 * 24 * 30)
    else:
        _DOC_STORE[key] = payload
