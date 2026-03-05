from __future__ import annotations

from functools import lru_cache

from ...core.logging import get_logger


RERANK_MODEL_ID = "BAAI/bge-reranker-base"


@lru_cache(maxsize=1)
def _cross_encoder():
    try:
        from sentence_transformers import CrossEncoder  # type: ignore
    except Exception as exc:  # pragma: no cover - import path depends on env
        get_logger().warning("Reranker unavailable: sentence-transformers missing (%s)", exc)
        return None

    try:
        return CrossEncoder(RERANK_MODEL_ID)
    except Exception as exc:  # pragma: no cover - model download/runtime depends on env
        get_logger().warning("Reranker model load failed (%s): %s", RERANK_MODEL_ID, exc)
        return None


def rerank_matches(question: str, matches: list[dict], top_k_final: int) -> list[dict]:
    if not matches:
        return []

    model = _cross_encoder()
    if model is None:
        return matches[:top_k_final]

    pairs = [[question, m.get("text", "")] for m in matches]
    try:
        scores = model.predict(pairs)
    except Exception as exc:
        get_logger().warning("Reranker scoring failed: %s", exc)
        return matches[:top_k_final]

    scored = []
    for idx, match in enumerate(matches):
        item = dict(match)
        item["rerank_score"] = float(scores[idx])
        scored.append(item)

    scored.sort(key=lambda m: m.get("rerank_score", 0.0), reverse=True)
    return scored[:top_k_final]

