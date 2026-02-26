from __future__ import annotations

from __future__ import annotations

import json
import logging
import time
import uuid
from typing import Any

from fastapi import Request

from .config import settings


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        base: dict[str, Any] = {
            "ts": time.time(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if hasattr(record, "extra") and isinstance(record.extra, dict):
            base.update(record.extra)
        return json.dumps(base, ensure_ascii=True)


def configure_logging() -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.setLevel(settings.log_level)
    root.handlers = [handler]


def request_id() -> str:
    return uuid.uuid4().hex


def log_request(request: Request, status_code: int, duration_ms: float, request_id_value: str) -> None:
    logger = logging.getLogger("api.access")
    logger.info(
        "request",
        extra={
            "extra": {
                "request_id": request_id_value,
                "method": request.method,
                "path": request.url.path,
                "status": status_code,
                "duration_ms": round(duration_ms, 2),
                "client_ip": request.client.host if request.client else "unknown",
            }
        },
    )
