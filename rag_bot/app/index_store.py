from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np

from . import config
from .documents import DocumentChunk


@dataclass(frozen=True)
class SearchResult:
    score: float
    text: str
    metadata: dict


def _import_faiss():
    try:
        import faiss
    except ImportError as exc:
        raise RuntimeError("Install faiss-cpu to use the vector index.") from exc
    return faiss


def build_index(chunks: list[DocumentChunk], embedding_model, index_dir: Path | None = None) -> dict:
    if not chunks:
        raise ValueError("No chunks found for indexing.")

    target_dir = index_dir or config.INDEX_DIR
    target_dir.mkdir(parents=True, exist_ok=True)

    start = time.perf_counter()
    vectors = embedding_model.embed_documents([chunk.text for chunk in chunks])
    faiss = _import_faiss()
    index = faiss.IndexFlatIP(vectors.shape[1])
    index.add(vectors)
    faiss.write_index(index, str(target_dir / "faiss.index"))

    metadata = [
        {
            "id": chunk.id,
            "text": chunk.text,
            "metadata": chunk.metadata,
        }
        for chunk in chunks
    ]
    (target_dir / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    elapsed = round(time.perf_counter() - start, 3)
    info = {
        "embedding": asdict(embedding_model.info),
        "chunk_count": len(chunks),
        "elapsed_seconds": elapsed,
        "index_type": "faiss.IndexFlatIP",
        "created_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    (target_dir / "index_info.json").write_text(
        json.dumps(info, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return info


class FaissSearchIndex:
    def __init__(self, embedding_model, index_dir: Path | None = None):
        self.embedding_model = embedding_model
        self.index_dir = index_dir or config.INDEX_DIR
        faiss = _import_faiss()
        self.index = faiss.read_index(str(self.index_dir / "faiss.index"))
        self.metadata = json.loads((self.index_dir / "metadata.json").read_text(encoding="utf-8"))

    def search(self, query: str, top_k: int = config.DEFAULT_TOP_K) -> list[SearchResult]:
        query_vector = self.embedding_model.embed_query(query).reshape(1, -1).astype("float32")
        scores, indices = self.index.search(query_vector, top_k)
        results: list[SearchResult] = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0:
                continue
            row = self.metadata[int(idx)]
            results.append(
                SearchResult(
                    score=float(score),
                    text=row["text"],
                    metadata=row["metadata"],
                )
            )
        return results

