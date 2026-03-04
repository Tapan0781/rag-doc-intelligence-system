from __future__ import annotations

from backend.app.services.ingest import document_store


def test_document_store_in_memory_fallback(monkeypatch) -> None:
    monkeypatch.setattr(document_store, "get_client", lambda: None)

    document_store.set_document_status("doc-1", status="processing", filename="a.pdf")
    status = document_store.get_document_metadata("doc-1")
    assert status is not None
    assert status["status"] == "processing"

    document_store.save_document_metadata(
        document_id="doc-1",
        filename="a.pdf",
        checksum_sha256="abc",
        page_count=1,
        chunk_count=2,
    )
    saved = document_store.get_document_metadata("doc-1")
    assert saved is not None
    assert saved["status"] == "completed"
