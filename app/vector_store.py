import os
from typing import List

import chromadb

from .config import settings
from .embeddings import get_embedder
from .chunking import chunk_text


class VectorStore:
    def __init__(self):
        os.makedirs(settings.chroma_dir, exist_ok=True)
        self._client = chromadb.PersistentClient(path=settings.chroma_dir)
        self.collection = self._client.get_or_create_collection(
            name=settings.collection_name, metadata={"hnsw:space": "cosine"}
        )
        self.embedder = get_embedder()

    def ingest(self, doc_id: str, text: str):
        chunks = chunk_text(text, settings.chunk_size, settings.chunk_overlap)
        if not chunks:
            return 0
        existing = self.collection.get(where={"doc_id": doc_id}, include=[])
        if existing and existing["ids"]:
            self.collection.delete(ids=existing["ids"])
        ids = [f"{doc_id}:{i}" for i in range(len(chunks))]
        embeddings = self.embedder.embed_texts(chunks)
        self.collection.upsert(
            ids=ids,
            documents=chunks,
            embeddings=embeddings,
            metadatas=[{"doc_id": doc_id, "chunk": i} for i in range(len(chunks))],
        )
        return len(chunks)

    def search(self, query: str, top_k: int, where: dict | None = None) -> List[dict]:
        q_vec = self.embedder.embed_texts([query])[0]
        kwargs = dict(query_embeddings=[q_vec], n_results=max(top_k * 2, top_k), include=["documents", "metadatas", "distances"])
        if where:
            kwargs["where"] = where
        results = self.collection.query(**kwargs)
        hits = []
        ids = results.get("ids", [[]])[0]
        docs = results.get("documents", [[]])[0]
        dists = results.get("distances", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        for i in range(len(ids)):
            hits.append({"id": ids[i], "text": docs[i], "score": 1.0 - dists[i], "metadata": metas[i]})
        return hits[:top_k]