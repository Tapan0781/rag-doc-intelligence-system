from __future__ import annotations

import json
from typing import Iterable

import requests

from ...core.config import settings
from ...core.errors import AppError


OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"


def _build_messages(question: str, contexts: Iterable[str]) -> list[dict[str, str]]:
    context_block = "\n\n".join(
        f"[{i + 1}] {chunk}" for i, chunk in enumerate(contexts)
    )

    developer_prompt = (
        "You are a careful assistant for a RAG system. "
        "Answer the question using ONLY the provided context. "
        "If the answer is not in the context, say you do not know."
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


def generate_answer(question: str, contexts: Iterable[str]) -> str:
    if not settings.openai_api_key:
        raise AppError("OPENAI_API_KEY is not set.", status_code=500, error_code="config_error")

    messages = _build_messages(question, contexts)
    payload = {
        "model": settings.llm_model,
        "messages": messages,
        "temperature": settings.llm_temperature,
        "max_tokens": settings.llm_max_output_tokens,
    }

    headers = {
        "Authorization": f"Bearer {settings.openai_api_key}",
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
