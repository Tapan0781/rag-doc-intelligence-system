from __future__ import annotations

from ...clients.redis import get_client


def get_cache(key: str) -> str | None:
    client = get_client()
    value = client.get(key)
    return value.decode("utf-8") if value else None


def set_cache(key: str, value: str, ttl_seconds: int = 3600) -> None:
    client = get_client()
    client.setex(key, ttl_seconds, value)
