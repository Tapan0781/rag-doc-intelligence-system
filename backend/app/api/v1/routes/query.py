from __future__ import annotations

from fastapi import APIRouter

from ...schemas.query import QueryRequest, QueryResponse
from ....services.rag.pipeline import answer_question

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
async def query_rag(request: QueryRequest) -> QueryResponse:
    answer, sources = answer_question(request.question, request.top_k)
    return QueryResponse(answer=answer, sources=sources)
