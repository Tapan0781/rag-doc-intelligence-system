from __future__ import annotations

import re


def normalize_text(text: str) -> str:
    return " ".join(text.split())


def clean_answer_text(text: str) -> str:
    cleaned = (text or "").strip()

    # Remove known trailing chunk/source id patterns.
    # Handle mixed trailing patterns like "[doc:1] (doc:2)".
    for _ in range(3):
        updated = re.sub(r"(?:\s*\[[0-9A-Za-z_.:-]{3,}\]\s*)+$", "", cleaned)
        updated = re.sub(r"(?:\s*\([0-9A-Za-z_.:-]{3,}\)\s*)+$", "", updated)
        if updated == cleaned:
            break
        cleaned = updated

    # Drop inline metadata fragments commonly leaked by model output.
    cleaned = re.sub(r"\b(?:chunk_id|source_id|document_id)\s*:\s*[0-9A-Za-z_.:-]+\b", "", cleaned, flags=re.IGNORECASE)

    # Remove empty/stray bracket artifacts while preserving normal text.
    cleaned = re.sub(r"\[\s*[,;:.-]*\s*\]", "", cleaned)
    cleaned = re.sub(r"\(\s*[,;:.-]*\s*\)", "", cleaned)

    # Remove dangling trailing brackets introduced by malformed citations.
    cleaned = re.sub(r"\s*[\[\(][^\]\)]{0,80}$", "", cleaned)

    return normalize_text(cleaned).strip(" \t\r\n,;")
