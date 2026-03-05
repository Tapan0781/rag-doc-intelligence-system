from __future__ import annotations

from backend.app.utils.text import clean_answer_text, normalize_text


def test_normalize_text_collapses_whitespace() -> None:
    raw = "This   is  a\n\n test\tstring."
    assert normalize_text(raw) == "This is a test string."


def test_clean_answer_removes_trailing_chunk_ids() -> None:
    raw = "AWS S3 is object storage. [doc-1:3] (doc-1:4)"
    assert clean_answer_text(raw) == "AWS S3 is object storage."


def test_clean_answer_removes_stray_metadata_and_brackets() -> None:
    raw = "Answer source_id: doc-9:2 chunk_id: c-2 [] ()"
    assert clean_answer_text(raw) == "Answer"
