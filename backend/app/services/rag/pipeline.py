from __future__ import annotations

from ...core.config import settings
from ...services.cache.redis import get_cache, set_cache
from ...services.llm.openai_chat import generate_answer
from ...services.retrieve.pinecone import query_similar


def _snippet(text: str, max_len: int = 220) -> str:
    text = " ".join((text or "").split())
    return text if len(text) <= max_len else text[: max_len - 1] + "…"


def _strip_trailing_citations(text: str) -> str:
    import re

    pattern = re.compile(r"(\\s*\\[[0-9a-fA-F-]{8,}:\\d+\\]\\s*)+$")
    return re.sub(pattern, "", text).strip()


def answer_question(
    question: str,
    top_k: int | None = None,
    model: str | None = None,
    api_key: str | None = None,
) -> tuple[str, list[dict], list[str], dict | None]:
    top_k = top_k or settings.max_query_results
    model_id = model or settings.llm_model
    cache_key = f"rag:query:{question.strip().lower()}:{top_k}:{model_id}"
    cached = get_cache(cache_key)
    if cached:
        source_ids = [s.get("source_id") for s in cached.get("sources", []) if s.get("source_id")]
        debug = cached.get("debug")
        return cached["answer"], cached["sources"], source_ids, debug

    matches = query_similar(question, top_k=top_k)

    min_score = settings.rag_min_score
    good = [m for m in matches if m.get("score", 0.0) >= min_score]

    sources_pretty: list[dict] = []
    for m in good[:5]:
        label_parts = []
        if m.get("filename"):
            label_parts.append(str(m["filename"]))
        if m.get("page") is not None:
            label_parts.append(f"p.{m['page']}")
        if m.get("chunk_index") is not None:
            label_parts.append(f"chunk {m['chunk_index']}")
        label_parts.append(f"score {m.get('score', 0.0):.2f}")

        sources_pretty.append(
            {
                "source_id": f"{m.get('id')}",
                "label": " • ".join(label_parts),
                "snippet": _snippet(m.get("text", "")),
            }
        )

    debug: dict | None = None
    if settings.rag_debug:
        debug = {
            "top_k": top_k,
            "min_score": min_score,
            "matches": [
                {
                    "chunk_id": m.get("id"),
                    "score": float(m.get("score", 0.0) or 0.0),
                    "preview": _snippet(m.get("text", ""), max_len=120),
                }
                for m in matches
            ],
        }

    if not good:
        answer = "I couldn't find relevant information in the uploaded document."
        set_cache(cache_key, {"answer": answer, "sources": [], "debug": debug})
        return answer, [], [], debug

    # LLM call uses ONLY retrieved contexts
    contexts = [
        (m.get("id") or f"{m.get('document_id','doc')}:{m.get('chunk_index','?')}", m.get("text", ""))
        for m in good[:5]
        if m.get("text")
    ]
    answer = generate_answer(question, contexts, model=model, api_key=api_key)
    answer = _strip_trailing_citations(answer)

    set_cache(cache_key, {"answer": answer, "sources": sources_pretty, "debug": debug})
    source_ids = [s.get("source_id") for s in sources_pretty if s.get("source_id")]
    return answer, sources_pretty, source_ids, debug
