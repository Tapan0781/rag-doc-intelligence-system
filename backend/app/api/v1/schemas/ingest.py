from __future__ import annotations

from pydantic import BaseModel


class IngestResponse(BaseModel):
    document_id: str
    chunks_created: int
