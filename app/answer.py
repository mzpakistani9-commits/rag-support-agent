import json
from typing import List

from .config import settings


def format_context(hits: List[dict]) -> str:
    parts = []
    for i, h in enumerate(hits):
        parts.append(f"[{i + 1}] {h['text']}")
    return "\n\n".join(parts)


def build_prompt(user_question: str, context: str) -> str:
    return (
        "You are a customer-support assistant that answers ONLY from the context below.\n"
        "If the context does not contain the answer, say exactly: TRIGGER_ESCALATION\n"
        "Quote the source chunk number in brackets like [1] when you use it.\n\n"
        f"CONTEXT:\n{context}\n\n"
        f"QUESTION: {user_question}\n\n"
        "ANSWER:"
    )


def answer_question(user_question: str, hits: List[dict]) -> dict:
    """Return dict with answer + sources + escalation flag."""
    top_score = hits[0]["similarity"] if hits else 0.0
    context = format_context(hits)
    need_llm = settings.openai_api_key and settings.embedding_provider == "openai"

    if need_llm:
        from openai import OpenAI

        client = OpenAI(api_key=settings.openai_api_key)
        prompt = build_prompt(user_question, context)
        resp = client.chat.completions.create(
            model=settings.openai_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
        )
        answer = (resp.choices[0].message.content or "").strip()
        escalated = "TRIGGER_ESCALATION" in answer or top_score < settings.escalation_threshold
        if escalated:
            answer = answer.replace("TRIGGER_ESCALATION", "").strip()
        return {"answer": answer, "sources": hits, "escalated": escalated, "confidence": round(top_score, 4)}

    # Fallback (no LLM key): extractive answer from the top chunk.
    extracted = hits[0]["text"] if hits else "I don't have enough information from the knowledge base."
    escalated = top_score < settings.escalation_threshold
    return {
        "answer": (
            "Based on the knowledge base:\n\n" + extracted
            if not escalated
            else "I don't have enough information from the knowledge base. A human agent will follow up."
        ),
        "sources": hits,
        "escalated": escalated,
        "confidence": round(top_score, 4),
    }


def stream_answer(user_question: str, hits: List[dict]):
    result = answer_question(user_question, hits)
    text = result["answer"]
    for token in text.split(" "):
        yield json.dumps({"token": token + " "}) + "\n"
    yield json.dumps({"done": True, "escalated": result["escalated"], "confidence": result["confidence"]}) + "\n"