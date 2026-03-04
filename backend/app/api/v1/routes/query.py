from __future__ import annotations

from fastapi import APIRouter

from ..schemas.query import QueryRequest, QueryResponse
from ....core.metrics import inc
from ....services.rag.pipeline import answer_question
from ....core.errors import AppError

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
async def query_rag(request: QueryRequest) -> QueryResponse:
    if not request.question.strip():
        raise AppError("Question must not be empty.", status_code=400, error_code="validation_error")
    inc("query_requests")
    answer, sources, source_ids, debug = answer_question(
        request.question,
        request.top_k,
        model=request.model,
        api_key=request.api_key,
    )
    return QueryResponse(answer=answer, sources=sources, source_ids=source_ids, debug=debug)
