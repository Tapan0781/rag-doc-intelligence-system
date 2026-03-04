from __future__ import annotations

from fastapi.testclient import TestClient

from backend.app.main import app


def test_query_response_includes_source_ids(monkeypatch) -> None:
    def _fake_answer_question(question: str, top_k=None):
        sources = [
            {"source_id": "doc-1:0", "label": "doc.pdf • p.1 • chunk 0 • score 0.90", "snippet": "text"},
            {"source_id": "doc-1:1", "label": "doc.pdf • p.1 • chunk 1 • score 0.80", "snippet": "more text"},
        ]
        return "answer", sources, ["doc-1:0", "doc-1:1"], None

    monkeypatch.setattr(
        "backend.app.api.v1.routes.query.answer_question",
        _fake_answer_question,
    )

    client = TestClient(app)
    response = client.post("/api/v1/query", json={"question": "What is Amazon S3 used for?"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["answer"] == "answer"
    assert payload["source_ids"] == ["doc-1:0", "doc-1:1"]
    assert len(payload["sources"]) == 2
