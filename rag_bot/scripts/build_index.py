from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app import config
from app.documents import build_chunks
from app.embeddings import create_embedding_model
from app.index_store import build_index


def main() -> None:
    parser = argparse.ArgumentParser(description="Build FAISS index for QuantumForge RAG bot.")
    parser.add_argument("--index-dir", type=Path, default=config.INDEX_DIR)
    parser.add_argument("--profile", choices=["default", "gapped"], default="default")
    parser.add_argument("--embedding-backend", default=config.DEFAULT_EMBEDDING_BACKEND)
    parser.add_argument("--no-malicious", action="store_true")
    args = parser.parse_args()

    chunks = build_chunks(include_malicious=not args.no_malicious, profile=args.profile)
    embedding_model = create_embedding_model(args.embedding_backend)
    info = build_index(chunks, embedding_model, args.index_dir)
    print(json.dumps(info, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

