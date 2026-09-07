import re
from typing import List, Set

from .vector_store import VectorStore

STOPWORDS: Set[str] = {
    "a", "an", "the", "and", "or", "of", "to", "in", "on", "for", "with", "at",
    "from", "by", "is", "are", "was", "were", "be", "this", "that", "these",
    "those", "what", "how", "when", "where", "who", "does", "do", "can", "you",
    "your", "my", "i", "me", "we", "it", "as", "than",
}


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def _keyword_overlap(query: str, doc: str) -> float:
    """Stopword-filtered lexical overlap. In offline mode this is the relevance gate."""
    qt = _tokens(query) - STOPWORDS
    dt = _tokens(doc) - STOPWORDS
    if not qt:
        return 0.0
    return len(qt & dt) / len(qt)


def hybrid_search(store: VectorStore, query: str, top_k: int, where: dict | None = None) -> List[dict]:
    """Fetch a wide candidate pool, rank it twice (vector + keyword), fuse with RRF."""
    # The hashing embedder's vectors are coarse, so a narrow fetch window can
    # miss keyword-relevant chunks before fusion ever sees them. Fetch a wider
    # candidate pool (settings.fetch_k) and return the fused top_k.
    from .config import settings

    fetch_k = max(top_k, settings.fetch_k)
    vec_hits = store.search(query, top_k=fetch_k, where=where)
    items = {h["id"]: h for h in vec_hits}
    for h in items.values():
        h["keyword"] = _keyword_overlap(query, h["text"])
        h["lexical"] = h["keyword"]

    vec_ranked = sorted(items.values(), key=lambda h: h["score"], reverse=True)
    kw_ranked = sorted(items.values(), key=lambda h: h["keyword"], reverse=True)

    vec_pos = {h["id"]: i for i, h in enumerate(vec_ranked)}
    kw_pos = {h["id"]: i for i, h in enumerate(kw_ranked)}

    for h in items.values():
        h["similarity"] = h["score"]
        h["score"] = (1.0 / (60 + vec_pos[h["id"]])) + (1.0 / (60 + kw_pos[h["id"]]))

    fused = sorted(items.values(), key=lambda h: h["score"], reverse=True)
    return fused[:top_k]