from __future__ import annotations

from io import BytesIO

from fastapi import UploadFile
from pypdf import PdfReader


def _extract_text(reader: PdfReader) -> str:
    parts: list[str] = []
    for page in reader.pages:
        text = page.extract_text() or ""
        if text:
            parts.append(text)
    return "\n".join(parts)


async def load_pdf_text(file: UploadFile) -> tuple[str, bytes, int]:
    data = await file.read()
    reader = PdfReader(BytesIO(data))
    text = _extract_text(reader)
    page_count = len(reader.pages)
    return text, data, page_count
