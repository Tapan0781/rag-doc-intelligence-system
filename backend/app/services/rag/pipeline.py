from __future__ import annotations

from ...services.cache.redis import get_cache, set_cache
from ...services.llm.openai_chat import generate_answer
from ...services.retrieve.pinecone import query_similar
from ...core.config import settings


def answer_question(question: str, top_k: int | None = None) -> tuple[str, list[str], list[str]]:
    cache_key = f"rag:query:{question.strip().lower()}:{top_k or settings.max_query_results}"
    cached = get_cache(cache_key)
    if cached:
        return cached, [], []

    contexts = query_similar(question, top_k=top_k)
    source_texts = [c.get("text", "") for c in contexts if c.get("text")]
    source_ids = [c.get("id") or f"{c.get('document_id','doc')}:{c.get('chunk_id','?')}" for c in contexts]
    paired_contexts = [
        (source_ids[i], source_texts[i])
        for i in range(min(len(source_ids), len(source_texts)))
        if source_texts[i]
    ]

    answer = (
        generate_answer(question, paired_contexts)
        if paired_contexts
        else "No relevant context found."
    )

    set_cache(cache_key, answer)
    return answer, source_texts, source_ids
