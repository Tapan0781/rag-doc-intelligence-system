from __future__ import annotations

import json
from typing import Iterable, Tuple

import requests

from ...core.config import settings
from ...core.errors import AppError


OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"


def _build_messages(
    question: str,
    contexts: Iterable[Tuple[str, str]],
) -> list[dict[str, str]]:
    context_block = "\n\n".join(
        f"[{source_id}] {chunk}" for source_id, chunk in contexts
    )

    developer_prompt = (
        "You are a strict document QA assistant. "
        "Use ONLY the provided context. "
        "Do NOT use outside knowledge. "
        "Do NOT fabricate facts. "
        "If the answer is not explicitly present in the context, respond exactly with: "
        "'Not found in the provided document.' "
        "Return ONLY the answer text. "
        "Do NOT include citations, chunk ids, brackets, metadata, or references."
    )

    user_prompt = (
        f"Context:\n{context_block}\n\n"
        f"Question: {question}\n\n"
        "Answer:"
    )

    return [
        {"role": "developer", "content": developer_prompt},
        {"role": "user", "content": user_prompt},
    ]


def generate_answer(
    question: str,
    contexts: Iterable[Tuple[str, str]],
    model: str | None = None,
    api_key: str | None = None,
) -> str:
    resolved_api_key = api_key or settings.openai_api_key
    if not resolved_api_key:
        raise AppError("OPENAI_API_KEY is not set.", status_code=500, error_code="config_error")

    messages = _build_messages(question, contexts)
    payload = {
        "model": model or settings.llm_model,
        "messages": messages,
        "temperature": settings.llm_temperature,
        "max_tokens": settings.llm_max_output_tokens,
    }

    headers = {
        "Authorization": f"Bearer {resolved_api_key}",
        "Content-Type": "application/json",
    }

    response = requests.post(
        OPENAI_API_URL,
        headers=headers,
        data=json.dumps(payload),
        timeout=60,
    )
    if response.status_code != 200:
        raise AppError(
            f"OpenAI API error {response.status_code}: {response.text}",
            status_code=502,
            error_code="upstream_error",
        )

    data = response.json()
    return data["choices"][0]["message"]["content"].strip()
