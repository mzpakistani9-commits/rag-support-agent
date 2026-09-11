"""Gradio demo for the RAG Support Agent.

Wraps the offline RAG pipeline in an interactive UI so visitors can
ask questions, ingest their own documents, and see citations — all
without needing an API key.
"""
import os
import sys

os.environ.setdefault("CHROMA_DIR", "/tmp/chroma_db")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import gradio as gr

from app.config import settings
from app.vector_store import VectorStore
from app.retrieval import hybrid_search
from app.answer import answer_question

store = VectorStore()


def _seed_if_empty():
    existing = store.collection.count()
    if existing:
        return
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "scripts"))
    from sample_docs import SAMPLE_DOCS

    for doc_id, text in SAMPLE_DOCS.items():
        store.ingest(doc_id, text)


_seed_if_empty()


def ask_question(question: str):
    if not question.strip():
        return "Please enter a question.", ""
    hits = hybrid_search(store, question, settings.top_k)
    result = answer_question(question, hits)
    source_lines = []
    for s in result["sources"]:
        meta = s.get("metadata", {})
        doc_id = meta.get("doc_id", s["id"])
        source_lines.append(f"- **{doc_id}** `rrf={s['score']:.3f}` — {s['text'][:110]}...")
    sources_text = "\n".join(source_lines) if source_lines else "_(no retrieved sources)_"
    badge = "\n\n⚠️ **Escalated to human** — low confidence (no grounded answer)" if result["escalated"] else f"\n\n*confidence: {result['confidence']}*"
    return result["answer"] + badge, sources_text


def ingest_doc(doc_id: str, text: str):
    if not doc_id.strip() or not text.strip():
        return "Provide both a doc_id and document text."
    n = store.ingest(doc_id, text)
    return f"Ingested `{doc_id}` — {n} chunks added. Ask about it below."


def health_check():
    return f"Status: OK | Provider: `{settings.embedding_provider}` | Collection: `{settings.collection_name}`"


with gr.Blocks(title="RAG Support Agent") as demo:
    gr.Markdown("# RAG Support Agent")
    gr.Markdown("Ask a question grounded in the knowledge base — or ingest your own documents and chat with them.")
    with gr.Tab("Ask"):
        q = gr.Textbox(label="Question", placeholder="How do I cancel my subscription?")
        ask_btn = gr.Button("Ask", variant="primary")
        answer_out = gr.Markdown(label="Answer")
        sources_out = gr.Markdown(label="Sources")
        gr.on([ask_btn.click, q.submit], ask_question, inputs=q, outputs=[answer_out, sources_out])
    with gr.Tab("Ingest"):
        doc_id_in = gr.Textbox(label="Document ID", placeholder="my_faq")
        text_in = gr.Textbox(label="Document text", lines=6, placeholder="Paste your support doc here...")
        ingest_btn = gr.Button("Ingest", variant="secondary")
        ingest_out = gr.Markdown()
        ingest_btn.click(ingest_doc, inputs=[doc_id_in, text_in], outputs=ingest_out)
    with gr.Tab("Health"):
        health_btn = gr.Button("Check")
        health_out = gr.Markdown()
        health_btn.click(health_check, outputs=health_out)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, theme=gr.themes.Soft())