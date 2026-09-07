import hashlib
import re
from typing import List

import numpy as np

from .config import settings


class LocalEmbedder:
    """Deterministic hashing embedder so the pipeline runs with no API keys."""

    DIM = 384

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        return [self._embed(t) for t in texts]

    def _embed(self, text: str) -> List[float]:
        vec = np.zeros(self.DIM, dtype=np.float32)
        tokens = re.findall(r"[a-z0-9]+", text.lower())
        features = list(tokens)
        features += ["".join(pair) for pair in zip(tokens, tokens[1:])]
        for feat in features:
            h = int.from_bytes(hashlib.md5(feat.encode()).digest()[:4], "little")
            vec[h % self.DIM] += 1.0
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec /= norm
        return vec.tolist()


class OpenAIEmbedder:
    def __init__(self):
        from openai import OpenAI

        self._client = OpenAI(api_key=settings.openai_api_key)

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        resp = self._client.embeddings.create(model=settings.embedding_model, input=texts)
        return [d.embedding for d in resp.data]


def get_embedder():
    if settings.embedding_provider == "openai" and settings.openai_api_key:
        return OpenAIEmbedder()
    return LocalEmbedder()