from __future__ import annotations

import redis

from ..core.config import settings
from ..core.logging import get_logger


_redis_client: redis.Redis | None = None
_redis_ready: bool | None = None


def get_client() -> redis.Redis | None:
    global _redis_client, _redis_ready
    if _redis_ready is False:
        return None
    if _redis_client is None:
        _redis_client = redis.Redis.from_url(settings.redis_url)
    try:
        _redis_client.ping()
        _redis_ready = True
        return _redis_client
    except Exception:
        _redis_ready = False
        get_logger().warning("Redis unavailable, using in-memory store.")
        return None
