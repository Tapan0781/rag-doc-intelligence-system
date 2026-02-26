from __future__ import annotations

import redis

from ..core.config import settings


_redis_client = redis.Redis.from_url(settings.redis_url)


def get_client() -> redis.Redis:
    return _redis_client
