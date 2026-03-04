from __future__ import annotations

from pydantic import BaseModel


class IngestResponse(BaseModel):
    document_id: str
    chunks_created: int
    filename: str
    checksum_sha256: str
    page_count: int


class IngestAsyncResponse(BaseModel):
    document_id: str
    status: str


class IngestStatusResponse(BaseModel):
    document_id: str
    status: str
    percent: int | None = None
    current: int | None = None
    total: int | None = None
    filename: str | None = None
    checksum_sha256: str | None = None
    page_count: int | None = None
    chunks_created: int | None = None
    error: str | None = None
    created_at: str | None = None
