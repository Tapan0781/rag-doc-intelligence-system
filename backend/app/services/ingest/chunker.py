from __future__ import annotations

import re
from collections import deque

from ....core.config import Chunk, settings


_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")


def _split_sentences(text: str) -> list[str]:
    text = " ".join(text.split())
    if not text:
        return []
    return [s.strip() for s in _SENTENCE_SPLIT.split(text) if s.strip()]


def chunk_text(
    text: str,
    document_id: str,
    extra_metadata: dict[str, str] | None = None,
) -> list[Chunk]:
    size = settings.chunk_size
    overlap = settings.chunk_overlap

    sentences = _split_sentences(text)
    if not sentences:
        return []

    chunks: list[Chunk] = []
    current: list[str] = []
    current_len = 0
    idx = 0
    overlap_buffer: deque[str] = deque()

    def flush() -> None:
        nonlocal idx, current, current_len
        if not current:
            return
        chunk_text_value = " ".join(current).strip()
        if not chunk_text_value:
            current.clear()
            current_len = 0
            return
        metadata = {"document_id": document_id, "chunk_id": str(idx)}
        if extra_metadata:
            metadata.update(extra_metadata)
        chunks.append(
            Chunk(
                id=f"{document_id}:{idx}",
                text=chunk_text_value,
                metadata=metadata,
            )
        )
        idx += 1
        # Prepare overlap buffer for next chunk.
        if overlap > 0:
            overlap_buffer.clear()
            total = 0
            for sentence in reversed(current):
                sentence_len = len(sentence)
                if total + sentence_len > overlap and total > 0:
                    break
                overlap_buffer.appendleft(sentence)
                total += sentence_len + 1
        else:
            overlap_buffer.clear()
        current = list(overlap_buffer)
        current_len = sum(len(s) for s in current) + max(len(current) - 1, 0)

    for sentence in sentences:
        sentence_len = len(sentence)
        if current_len + sentence_len + (1 if current else 0) > size:
            flush()
        if sentence_len > size:
            # Hard split long sentences to avoid empty chunks.
            start = 0
            while start < sentence_len:
                part = sentence[start : start + size]
                if part:
                    current = list(overlap_buffer)
                    if current:
                        current_len = sum(len(s) for s in current) + len(current) - 1
                    else:
                        current_len = 0
                    current.append(part)
                    current_len += len(part) + (1 if current_len else 0)
                    flush()
                start += size
            continue
        if current:
            current_len += 1
        current.append(sentence)
        current_len += sentence_len

    flush()
    return chunks
