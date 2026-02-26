from __future__ import annotations

from fastapi import APIRouter

from ....core.metrics import snapshot

router = APIRouter()


@router.get("/health")
async def health() -> dict:
    return {"status": "ok", "metrics": snapshot()}
