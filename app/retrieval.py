import re
from typing import List

from .vector_store import VectorStore


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def _keyword_overlap(query: str, doc: str) -> float:
    qt, dt = _tokens(query), _tokens(doc)
    if not qt:
        return 0.0
    return len(qt & dt) / len(qt)


def hybrid_search(store: VectorStore, query: str, top_k: int, where: dict | None = None) -> List[dict]:
    """Fetch one list, rank it twice (vector + keyword), fuse with Reciprocal Rank Fusion."""
    vec_hits = store.search(query, top_k=top_k, where=where)
    items = {h["id"]: h for h in vec_hits}
    for h in items.values():
        h["keyword"] = _keyword_overlap(query, h["text"])

    vec_ranked = sorted(items.values(), key=lambda h: h["score"], reverse=True)
    kw_ranked = sorted(items.values(), key=lambda h: h["keyword"], reverse=True)

    vec_pos = {h["id"]: i for i, h in enumerate(vec_ranked)}
    kw_pos = {h["id"]: i for i, h in enumerate(kw_ranked)}

    for h in items.values():
        h["similarity"] = h["score"]
        h["score"] = (1.0 / (60 + vec_pos[h["id"]])) + (1.0 / (60 + kw_pos[h["id"]]))

    fused = sorted(items.values(), key=lambda h: h["score"], reverse=True)
    return fused[:top_k]