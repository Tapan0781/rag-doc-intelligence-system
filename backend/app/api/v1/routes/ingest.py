from __future__ import annotations

import hashlib
import uuid

from fastapi import APIRouter, BackgroundTasks, UploadFile

from ...schemas.ingest import IngestAsyncResponse, IngestResponse, IngestStatusResponse
from ....core.errors import AppError
from ....core.metrics import inc
from ....services.embed.fastembed import embed_texts
from ....services.ingest.chunker import chunk_text
from ....services.ingest.document_store import save_document_metadata
from ....services.ingest.document_store import get_document_metadata, set_document_status
from ....services.ingest.job_runner import run_ingest_job
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


@router.post("/ingest/async", response_model=IngestAsyncResponse)
async def ingest_pdf_async(
    file: UploadFile, background_tasks: BackgroundTasks
) -> IngestAsyncResponse:
    if file.content_type != "application/pdf":
        raise AppError("Only PDF files are supported.", status_code=415, error_code="unsupported_media_type")
    inc("ingest_requests")
    document_id = str(uuid.uuid4())
    filename = file.filename or "document.pdf"
    file_bytes = await file.read()
    if not file_bytes:
        raise AppError("Empty file.", status_code=400, error_code="validation_error")
    set_document_status(document_id, status="pending", filename=filename)
    background_tasks.add_task(run_ingest_job, file_bytes, filename, document_id)
    return IngestAsyncResponse(document_id=document_id, status="pending")


@router.get("/ingest/status/{document_id}", response_model=IngestStatusResponse)
async def ingest_status(document_id: str) -> IngestStatusResponse:
    data = get_document_metadata(document_id)
    if not data:
        raise AppError("Document not found.", status_code=404, error_code="not_found")
    return IngestStatusResponse(**data)
