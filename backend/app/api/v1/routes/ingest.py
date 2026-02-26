from __future__ import annotations

import hashlib
import uuid

from fastapi import APIRouter, UploadFile

from ...schemas.ingest import IngestResponse
from ....core.errors import AppError
from ....core.metrics import inc
from ....services.embed.fastembed import embed_texts
from ....services.ingest.chunker import chunk_text
from ....services.ingest.document_store import save_document_metadata
from ....services.ingest.loader import load_pdf_text
from ....services.retrieve.pinecone import upsert_chunks

router = APIRouter()


@router.post("/ingest", response_model=IngestResponse)
async def ingest_pdf(file: UploadFile) -> IngestResponse:
    if file.content_type != "application/pdf":
        raise AppError("Only PDF files are supported.", status_code=415, error_code="unsupported_media_type")
    inc("ingest_requests")
    document_id = str(uuid.uuid4())
    raw_text, file_bytes, page_count = await load_pdf_text(file)
    checksum_sha256 = hashlib.sha256(file_bytes).hexdigest()
    filename = file.filename or "document.pdf"
    extra_metadata = {
        "filename": filename,
        "checksum_sha256": checksum_sha256,
    }
    chunks = chunk_text(
        raw_text,
        document_id=document_id,
        extra_metadata=extra_metadata,
    )
    embeddings = embed_texts([c.text for c in chunks])
    upsert_chunks(chunks, embeddings)
    save_document_metadata(
        document_id=document_id,
        filename=filename,
        checksum_sha256=checksum_sha256,
        page_count=page_count,
        chunk_count=len(chunks),
    )
    return IngestResponse(
        document_id=document_id,
        chunks_created=len(chunks),
        filename=filename,
        checksum_sha256=checksum_sha256,
        page_count=page_count,
    )
