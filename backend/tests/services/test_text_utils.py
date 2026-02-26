from __future__ import annotations

from backend.app.utils.text import normalize_text


def test_normalize_text_collapses_whitespace() -> None:
    raw = "This   is  a\\n\\n test\\tstring."
    assert normalize_text(raw) == "This is a test string."
