from __future__ import annotations

from fastapi import Header

from .config import settings
from .errors import AppError


def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    if not settings.api_key:
        return
    if not x_api_key or x_api_key != settings.api_key:
        raise AppError("Invalid API key.", status_code=401, error_code="unauthorized")
