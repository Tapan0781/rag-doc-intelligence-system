from __future__ import annotations

from backend.app.services.ingest.chunker import chunk_text


def test_chunker_returns_chunks() -> None:
    text = (
        "Sentence one. Sentence two is a bit longer. "
        "Sentence three. Sentence four. Sentence five."
    )
    chunks = chunk_text(text, document_id="doc-1")
    assert chunks
    assert chunks[0].metadata["document_id"] == "doc-1"
    assert chunks[0].metadata["chunk_id"] == "0"


def test_chunker_includes_extra_metadata() -> None:
    text = "Sentence one. Sentence two. Sentence three."
    chunks = chunk_text(
        text,
        document_id="doc-2",
        extra_metadata={"filename": "sample.pdf"},
    )
    assert chunks
    assert chunks[0].metadata["filename"] == "sample.pdf"
