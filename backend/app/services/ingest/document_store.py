from __future__ import annotations

import json
from datetime import datetime, timezone

from ...clients.redis import get_client


def save_document_metadata(
    document_id: str,
    filename: str,
    checksum_sha256: str,
    page_count: int,
    chunk_count: int,
) -> None:
    client = get_client()
    payload = {
        "document_id": document_id,
        "filename": filename,
        "checksum_sha256": checksum_sha256,
        "page_count": page_count,
        "chunk_count": chunk_count,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    key = f"rag:doc:{document_id}"
    client.set(key, json.dumps(payload), ex=60 * 60 * 24 * 30)


def get_document_metadata(document_id: str) -> dict | None:
    client = get_client()
    key = f"rag:doc:{document_id}"
    raw = client.get(key)
    if not raw:
        return None
    return json.loads(raw.decode("utf-8"))
