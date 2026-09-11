"""Minimal FastAPI wrapper for Render deployment.

This file is Render's entry point. It re-exports the existing app
from app.main and adds startup seeding so the demo works immediately.
"""
import os
import sys

os.environ.setdefault("CHROMA_DIR", "/tmp/chroma_db")
sys.path.insert(0, os.path.dirname(__file__))

from app.main import app, store  # noqa: E402
from app.config import settings  # noqa: E402


@app.on_event("startup")
def seed_on_startup():
    if store.collection.count():
        return
    from scripts.sample_docs import SAMPLE_DOCS
    for doc_id, text in SAMPLE_DOCS.items():
        store.ingest(doc_id, text)
    print(f"Seeded {store.collection.count()} chunks on startup")