from __future__ import annotations

import hashlib
import time

from ...core.errors import AppError
from ..embed.fastembed import embed_texts
from ..retrieve.pinecone import upsert_chunks
from .chunker import chunk_pages
from .document_store import save_document_metadata, set_document_status


def _ingest_once(file_bytes: bytes, filename: str, document_id: str) -> None:
    pages, file_bytes, page_count = load_pdf_pages_sync(file_bytes)
    checksum_sha256 = hashlib.sha256(file_bytes).hexdigest()
    chunks = chunk_pages(
        pages,
        document_id=document_id,
        filename=filename,
    )
    total_chunks = len(chunks)
    set_document_status(
        document_id,
        status="processing",
        filename=filename,
        progress_current_chunks=0,
        progress_total_chunks=total_chunks,
    )
    embeddings = embed_texts([c.text for c in chunks])
    batch_size = 50
    for start in range(0, total_chunks, batch_size):
        end = min(start + batch_size, total_chunks)
        upsert_chunks(chunks[start:end], embeddings[start:end])
        set_document_status(
            document_id,
            status="processing",
            filename=filename,
            progress_current_chunks=end,
            progress_total_chunks=total_chunks,
        )
    save_document_metadata(
        document_id=document_id,
        filename=filename,
        checksum_sha256=checksum_sha256,
        page_count=page_count,
        chunk_count=len(chunks),
    )


def load_pdf_pages_sync(file_bytes: bytes) -> tuple[list[str], bytes, int]:
    if not file_bytes:
        raise AppError("Empty file.", status_code=400, error_code="validation_error")
    from pypdf import PdfReader
    from io import BytesIO

    reader = PdfReader(BytesIO(file_bytes))
    parts: list[str] = []
    for page in reader.pages:
        parts.append(page.extract_text() or "")
    return parts, file_bytes, len(reader.pages)


def run_ingest_job(file_bytes: bytes, filename: str, document_id: str, retries: int = 2) -> None:
    set_document_status(document_id, status="processing", filename=filename)
    attempt = 0
    while True:
        try:
            _ingest_once(file_bytes, filename, document_id)
            return
        except Exception as exc:
            attempt += 1
            if attempt > retries:
                set_document_status(
                    document_id,
                    status="failed",
                    error=str(exc),
                    filename=filename,
                )
                return
            time.sleep(1 + attempt)
