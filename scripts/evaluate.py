GOLD_QA = {
    "How long does standard shipping take?": "shipping_policy",
    "Do you offer free shipping?": "shipping_policy",
    "What is your refund window?": "refund_policy",
    "Are digital products refundable?": "refund_policy",
    "How do I reset my password?": "account_password",
    "Does the reset link expire?": "account_password",
    "How do I download an invoice?": "billing_and_invoices",
    "What happens if my card expires?": "billing_and_invoices",
    "What are the rate limits on the Standard plan?": "api_rate_limits",
    "What HTTP code do I get when rate limited?": "api_rate_limits",
    "How do I verify a webhook signature?": "integration_webhooks",
    "How many retries for a failed webhook?": "integration_webhooks",
    "What are the support hours?": "support_hours",
    "How do I contact enterprise support?": "support_hours",
    "What does the Professional plan cost?": "subscription_plans",
    "Can I cancel my subscription anytime?": "subscription_plans",
}

QUERIES_WITHOUT_ANSWER = [
    "What discount codes are active this week?",
    "Who founded the company in 1990?",
]


import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

def evaluate():
    from app.main import store
    from app.answer import answer_question
    from app.retrieval import hybrid_search
    from app.config import settings

    correct = 0
    escalation_false_negatives = 0
    rows = []
    for question, gold_doc in GOLD_QA.items():
        hits = hybrid_search(store, question, settings.top_k)
        hit_docs = {h["metadata"].get("doc_id") for h in hits}
        is_hit = gold_doc in hit_docs
        correct += int(is_hit)
        rows.append((question, gold_doc, sorted(hit_docs), is_hit))

    hit_rate = correct / len(GOLD_QA)
    for q in QUERIES_WITHOUT_ANSWER:
        result = answer_question(q, hybrid_search(store, q, settings.top_k))
        if result["escalated"] is False:
            escalation_false_negatives += 1

    print("\n=== RAG Retrieval Evaluation ===")
    for question, gold, got, ok in rows:
        print(f"  {'PASS' if ok else 'FAIL'}  {question}")
        print(f"        gold={gold}  got={got}")
    for q in QUERIES_WITHOUT_ANSWER:
        result = answer_question(q, hybrid_search(store, q, settings.top_k))
        print(f"  {'PASS' if result['escalated'] else 'FAIL'}  escalation check: {q}")

    print(f"\nRetrieval hit@k: {hit_rate:.0%} ({correct}/{len(GOLD_QA)})")
    print(f"Correct escalation for out-of-KB questions: {len(QUERIES_WITHOUT_ANSWER) - escalation_false_negatives}/{len(QUERIES_WITHOUT_ANSWER)}")
    print(
        "Quality gate: "
        + ("PASS" if hit_rate >= 0.8 and escalation_false_negatives == 0 else "FAILED")
    )
    return hit_rate


if __name__ == "__main__":
    evaluate()