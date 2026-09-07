import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))

from sample_docs import SAMPLE_DOCS
from app.main import store

RESET = False


def main():
    if RESET:
        store.collection.delete()
    total = 0
    for doc_id, text in SAMPLE_DOCS.items():
        n = store.ingest(doc_id, text)
        print(f"  ingested {doc_id}: {n} chunks")
        total += n
    print(f"Done. {total} chunks in collection '{store.collection.name}'")


if __name__ == "__main__":
    main()