from __future__ import annotations

from io import BytesIO

from fastapi import UploadFile
from pypdf import PdfReader


async def load_pdf_pages(file: UploadFile) -> tuple[list[str], bytes, int]:
    data = await file.read()
    reader = PdfReader(BytesIO(data))
    pages: list[str] = []
    for page in reader.pages:
        pages.append(page.extract_text() or "")
    page_count = len(reader.pages)
    return pages, data, page_count
