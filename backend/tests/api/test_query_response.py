from __future__ import annotations

import asyncio

from backend.app.api.v1.routes.query import query_rag
from backend.app.api.v1.schemas.query import QueryRequest
from backend.app.services.rag.pipeline import answer_question


def test_query_response_includes_source_ids(monkeypatch) -> None:
    def _fake_answer_question(question: str, top_k=None, model=None, api_key=None):
        sources = [
            {"source_id": "doc-1:0", "label": "doc.pdf • p.1 • chunk 0 • score 0.90", "snippet": "text"},
            {"source_id": "doc-1:1", "label": "doc.pdf • p.1 • chunk 1 • score 0.80", "snippet": "more text"},
        ]
        return "answer", sources, ["doc-1:0", "doc-1:1"], None

    monkeypatch.setattr(
        "backend.app.api.v1.routes.query.answer_question",
        _fake_answer_question,
    )

    response = asyncio.run(query_rag(QueryRequest(question="What is Amazon S3 used for?")))
    payload = response.model_dump()
    assert payload["answer"] == "answer"
    assert payload["source_ids"] == ["doc-1:0", "doc-1:1"]
    assert len(payload["sources"]) == 2
    assert set(payload.keys()) == {"answer", "sources", "source_ids", "debug"}


def test_low_retrieval_score_returns_not_found(monkeypatch) -> None:
    monkeypatch.setattr("backend.app.services.rag.pipeline.get_cache", lambda *_: None)
    monkeypatch.setattr("backend.app.services.rag.pipeline.set_cache", lambda *_, **__: None)
    monkeypatch.setattr(
        "backend.app.services.rag.pipeline.query_similar",
        lambda *_args, **_kwargs: [{"id": "doc-1:0", "score": 0.05, "text": "irrelevant"}],
    )

    answer, sources, source_ids, debug = answer_question("What is the SLA?")
    assert answer == "Not found in the provided document."
    assert sources == []
    assert source_ids == []
    assert debug is None
