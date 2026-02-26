from __future__ import annotations

import time
from collections import deque

from fastapi import Request

from ..clients.redis import get_client
from .config import settings
from .errors import AppError


_LOCAL_BUCKETS: dict[str, deque[float]] = {}


def _local_allow(key: str, limit: int, window_seconds: int) -> bool:
    now = time.time()
    bucket = _LOCAL_BUCKETS.setdefault(key, deque())
    while bucket and (now - bucket[0]) > window_seconds:
        bucket.popleft()
    if len(bucket) >= limit:
        return False
    bucket.append(now)
    return True


def _redis_allow(key: str, limit: int, window_seconds: int) -> bool:
    client = get_client()
    now = int(time.time())
    window_start = now - window_seconds
    pipe = client.pipeline()
    pipe.zremrangebyscore(key, 0, window_start)
    pipe.zadd(key, {str(now): now})
    pipe.zcard(key)
    pipe.expire(key, window_seconds)
    _, _, count, _ = pipe.execute()
    return int(count) <= limit


def enforce_rate_limit(request: Request) -> None:
    limit = settings.rate_limit_requests
    window = settings.rate_limit_window_seconds
    if limit <= 0:
        return

    client_ip = request.client.host if request.client else "unknown"
    key = f"ratelimit:{client_ip}"

    try:
        allowed = _redis_allow(key, limit, window)
    except Exception:
        allowed = _local_allow(key, limit, window)

    if not allowed:
        raise AppError(
            "Rate limit exceeded. Try again later.",
            status_code=429,
            error_code="rate_limited",
        )
