from __future__ import annotations

import uuid

from fastapi import APIRouter, UploadFile

from ...schemas.ingest import IngestResponse
from ....services.embed.fastembed import embed_texts
from ....services.ingest.chunker import chunk_text
from ....services.ingest.loader import load_pdf_text
from ....services.retrieve.pinecone import upsert_chunks

router = APIRouter()


@router.post("/ingest", response_model=IngestResponse)
async def ingest_pdf(file: UploadFile) -> IngestResponse:
    document_id = str(uuid.uuid4())
    raw_text = await load_pdf_text(file)
    chunks = chunk_text(raw_text, document_id=document_id)
    embeddings = embed_texts([c.text for c in chunks])
    upsert_chunks(chunks, embeddings)
    return IngestResponse(document_id=document_id, chunks_created=len(chunks))
