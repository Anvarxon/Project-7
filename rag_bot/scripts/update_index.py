from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app import config
from app.documents import build_chunks, file_hash, iter_document_paths
from app.embeddings import create_embedding_model
from app.index_store import build_index


def _load_manifest(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _write_log(path: Path, record: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as sink:
        sink.write(json.dumps(record, ensure_ascii=False) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Daily FAISS index updater.")
    parser.add_argument("--index-dir", type=Path, default=config.INDEX_DIR)
    parser.add_argument("--log-file", type=Path, default=config.LOG_DIR / "update_index.jsonl")
    parser.add_argument("--embedding-backend", default=config.DEFAULT_EMBEDDING_BACKEND)
    args = parser.parse_args()

    started = time.time()
    manifest_path = args.index_dir / "manifest.json"
    previous = _load_manifest(manifest_path)
    current = {str(path.relative_to(config.PROJECT_DIR)): file_hash(path) for path in iter_document_paths()}
    changed = sorted(path for path, digest in current.items() if previous.get(path) != digest)
    removed = sorted(path for path in previous if path not in current)

    try:
        chunks = build_chunks(include_malicious=True)
        embedding_model = create_embedding_model(args.embedding_backend)
        info = build_index(chunks, embedding_model, args.index_dir)
        args.index_dir.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(json.dumps(current, ensure_ascii=False, indent=2), encoding="utf-8")
        record = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "status": "updated",
            "changed_files": changed,
            "removed_files": removed,
            "new_or_changed_files_count": len(changed),
            "chunk_count": info["chunk_count"],
            "index_dir": str(args.index_dir),
            "elapsed_seconds": round(time.time() - started, 3),
            "errors": [],
        }
    except Exception as exc:
        record = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "status": "failed",
            "changed_files": changed,
            "removed_files": removed,
            "elapsed_seconds": round(time.time() - started, 3),
            "errors": [repr(exc)],
        }
        _write_log(args.log_file, record)
        raise

    _write_log(args.log_file, record)
    print(json.dumps(record, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

