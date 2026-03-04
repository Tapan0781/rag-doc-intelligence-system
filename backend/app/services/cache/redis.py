from __future__ import annotations

import json
from typing import Any

from ...clients.redis import get_client


def get_cache(key: str) -> Any | None:
    client = get_client()
    if not client:
        return None
    value = client.get(key)
    if not value:
        return None
    decoded = value.decode("utf-8")
    try:
        return json.loads(decoded)
    except json.JSONDecodeError:
        return decoded


def set_cache(key: str, value: Any, ttl_seconds: int = 3600) -> None:
    client = get_client()
    if not client:
        return
    payload = value if isinstance(value, str) else json.dumps(value)
    client.setex(key, ttl_seconds, payload)
