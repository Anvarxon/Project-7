from __future__ import annotations

import hashlib
import math
import re
from dataclasses import dataclass

import numpy as np

from . import config


TOKEN_PATTERN = re.compile(r"[a-zа-яё0-9][a-zа-яё0-9'\-]*", re.IGNORECASE)


@dataclass(frozen=True)
class EmbeddingInfo:
    backend: str
    model_name: str
    dimension: int


class HashingEmbeddingModel:
    """Deterministic local embedding fallback for demos without model downloads."""

    def __init__(self, dimension: int = config.DEFAULT_EMBEDDING_DIM):
        self.dimension = dimension
        self.info = EmbeddingInfo(
            backend="hashing",
            model_name=f"local-hashing-{dimension}",
            dimension=dimension,
        )

    def embed_documents(self, texts: list[str]) -> np.ndarray:
        return np.vstack([self.embed_query(text) for text in texts]).astype("float32")

    def embed_query(self, text: str) -> np.ndarray:
        vector = np.zeros(self.dimension, dtype="float32")
        tokens = [token.lower() for token in TOKEN_PATTERN.findall(text)]

        features: list[tuple[str, float]] = []
        features.extend((token, 1.0) for token in tokens)
        features.extend((f"{left}_{right}", 0.8) for left, right in zip(tokens, tokens[1:]))

        compact = " ".join(tokens)
        if len(compact) >= 3:
            features.extend((compact[i : i + 3], 0.18) for i in range(len(compact) - 2))

        for feature, weight in features:
            digest = hashlib.blake2b(feature.encode("utf-8"), digest_size=8).digest()
            number = int.from_bytes(digest, "little", signed=False)
            index = number % self.dimension
            sign = 1.0 if (number >> 9) & 1 else -1.0
            vector[index] += sign * weight

        norm = math.sqrt(float(np.dot(vector, vector)))
        if norm > 0:
            vector /= norm
        return vector.astype("float32")


class SentenceTransformerEmbeddingModel:
    def __init__(self, model_name: str = config.DEFAULT_EMBEDDING_MODEL):
        from sentence_transformers import SentenceTransformer

        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        dimension = int(self.model.get_sentence_embedding_dimension())
        self.info = EmbeddingInfo(
            backend="sentence-transformers",
            model_name=model_name,
            dimension=dimension,
        )

    def embed_documents(self, texts: list[str]) -> np.ndarray:
        return self.model.encode(texts, normalize_embeddings=True).astype("float32")

    def embed_query(self, text: str) -> np.ndarray:
        return self.model.encode([text], normalize_embeddings=True)[0].astype("float32")


def create_embedding_model(backend: str | None = None):
    selected = (backend or config.DEFAULT_EMBEDDING_BACKEND).lower()
    if selected in {"sentence-transformers", "sbert"}:
        return SentenceTransformerEmbeddingModel()
    if selected == "auto":
        try:
            return SentenceTransformerEmbeddingModel()
        except Exception:
            return HashingEmbeddingModel()
    if selected == "hashing":
        return HashingEmbeddingModel()
    raise ValueError(f"Unsupported embedding backend: {selected}")

