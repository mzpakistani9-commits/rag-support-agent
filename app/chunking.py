from typing import List


def chunk_text(text: str, chunk_size: int, overlap: int) -> List[str]:
    """Split text into overlapping chunks on paragraph/sentence boundaries."""
    text = text.strip()
    if not text:
        return []

    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks: List[str] = []
    current = ""
    for p in paragraphs:
        if len(current) + len(p) + 2 <= chunk_size:
            current = f"{current}\n\n{p}" if current else p
            continue
        if current:
            chunks.append(current)
        if len(p) > chunk_size:
            chunks.extend(_hard_split(p, chunk_size, overlap))
            current = ""
        else:
            current = p
    if current:
        chunks.append(current)

    if overlap > 0 and len(chunks) > 1:
        merged: List[str] = []
        for c in chunks:
            if merged:
                prev = merged[-1]
                merged[-1] = f"{prev}\n{prev[-overlap:]}"
            merged.append(c)
        chunks = merged

    return [c for c in chunks if c.strip()]


def _hard_split(text: str, chunk_size: int, overlap: int) -> List[str]:
    parts: List[str] = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        if end < len(text):
            cutoff = text.rfind(" ", start, end)
            if cutoff > start + chunk_size // 2:
                end = cutoff
        parts.append(text[start:end].strip())
        step = chunk_size - overlap if overlap > 0 else chunk_size
        start = start + step
    return [p for p in parts if p]