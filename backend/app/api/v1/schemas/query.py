from __future__ import annotations

from pydantic import BaseModel


class SourceItem(BaseModel):
    source_id: str
    label: str
    snippet: str


class DebugMatch(BaseModel):
    chunk_id: str | None = None
    score: float | None = None
    preview: str | None = None


class QueryDebug(BaseModel):
    top_k: int
    min_score: float
    matches: list[DebugMatch]


class QueryRequest(BaseModel):
    question: str
    top_k: int | None = None
    model: str | None = None
    api_key: str | None = None


class QueryResponse(BaseModel):
    answer: str
    sources: list[SourceItem]
    source_ids: list[str]
    debug: QueryDebug | None = None
