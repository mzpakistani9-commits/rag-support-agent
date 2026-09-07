from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from .config import settings
from .vector_store import VectorStore
from .retrieval import hybrid_search
from .answer import answer_question, stream_answer

app = FastAPI(title="RAG Support Agent", version="1.0.0")
store = VectorStore()


class IngestRequest(BaseModel):
    doc_id: str
    text: str


class AskRequest(BaseModel):
    question: str


@app.get("/health")
def health():
    return {"status": "ok", "collection": settings.collection_name, "provider": settings.embedding_provider}


@app.post("/ingest")
def ingest(req: IngestRequest):
    if not req.doc_id.strip():
        return {"error": "doc_id required"}
    n = store.ingest(req.doc_id, req.text)
    return {"doc_id": req.doc_id, "chunks": n}


@app.get("/ask")
def ask(question: str):
    hits = hybrid_search(store, question, settings.top_k)
    result = answer_question(question, hits)
    return {**result, "question": question}


@app.post("/ask")
def ask_post(req: AskRequest):
    hits = hybrid_search(store, req.question, settings.top_k)
    result = answer_question(req.question, hits)
    return {**result, "question": req.question}


@app.get("/ask/stream")
def ask_stream(question: str):
    hits = hybrid_search(store, question, settings.top_k)
    return StreamingResponse(stream_answer(question, hits), media_type="application/x-ndjson")