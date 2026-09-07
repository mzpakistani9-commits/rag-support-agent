import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

os.environ.setdefault("CHROMA_DIR", "/tmp/rag_test_chroma")

from app.chunking import chunk_text
from app.embeddings import LocalEmbedder
from app.vector_store import VectorStore
from app.retrieval import hybrid_search
from app.config import settings


def test_chunking_respects_size_and_overlap():
    text = "Alpha beta gamma." * 50
    chunks = chunk_text(text, 200, 30)
    assert len(chunks) >= 2
    assert all(len(c) <= 260 for c in chunks)


def test_chunking_empty():
    assert chunk_text("   ", 100, 10) == []


def test_local_embeddings_are_normalized():
    emb = LocalEmbedder()
    vecs = emb.embed_texts(["hello world", "another text"])
    assert len(vecs) == 2
    assert len(vecs[0]) == 384
    norm = sum(v**2 for v in vecs[0]) ** 0.5
    assert abs(norm - 1.0) < 0.02


def test_ingest_and_search_finds_similar_content():
    store = VectorStore()
    store.ingest("a", "Shipping takes three to five business days with tracked courier.")
    store.ingest("b", "Cats like to sleep in warm sunny places during the afternoon.")
    hits = hybrid_search(store, "how long does domestic shipping take?", settings.top_k)
    assert hits
    assert hits[0]["metadata"]["doc_id"] == "a"


def test_ingest_replace_same_doc():
    store = VectorStore()
    store.ingest("dup", "Original content one.")
    store.ingest("dup", "Replacement content two three four five six seven.")
    hits = store.search("replacement content two three four", top_k=2)
    assert hits and hits[0]["text"].startswith("Replacement")