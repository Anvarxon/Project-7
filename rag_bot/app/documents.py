from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from . import config
from .security import has_prompt_injection


GAP_TERMS = ("xarn velgor", "void core", "synth flux")


@dataclass(frozen=True)
class DocumentChunk:
    id: str
    text: str
    metadata: dict


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_terms_map(path: Path | None = None) -> dict[str, str]:
    terms_path = path or config.DATA_DIR / "terms_map.json"
    if not terms_path.exists():
        return {}
    return json.loads(terms_path.read_text(encoding="utf-8"))


def iter_document_paths(
    knowledge_dir: Path | None = None,
    include_malicious: bool = True,
    exclude_names: Iterable[str] | None = None,
) -> list[Path]:
    base_dir = knowledge_dir or config.KNOWLEDGE_DIR
    excluded = {name.lower() for name in (exclude_names or [])}
    paths = [
        path
        for path in sorted(base_dir.glob("*.md"))
        if path.name.lower() not in excluded and path.stem.lower() not in excluded
    ]

    if include_malicious and config.MALICIOUS_FILE.exists():
        paths.append(config.MALICIOUS_FILE)

    return paths


def read_title_and_body(path: Path) -> tuple[str, str]:
    text = path.read_text(encoding="utf-8").strip()
    title = path.stem.replace("_", " ").title()
    lines = text.splitlines()
    if lines and lines[0].startswith("#"):
        title = lines[0].lstrip("#").strip()
        body = "\n".join(lines[1:]).strip()
    else:
        body = text
    return title, body


def split_text(text: str, chunk_size: int, chunk_overlap: int) -> list[str]:
    try:
        from langchain_text_splitters import RecursiveCharacterTextSplitter

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", "; ", ", ", " "],
        )
        chunks = splitter.split_text(text)
        return [chunk.strip() for chunk in chunks if chunk.strip()]
    except Exception:
        words = re.findall(r"\S+", text)
        if not words:
            return []
        approx_words = max(80, chunk_size // 7)
        overlap_words = max(10, chunk_overlap // 7)
        chunks: list[str] = []
        start = 0
        while start < len(words):
            stop = min(len(words), start + approx_words)
            chunks.append(" ".join(words[start:stop]))
            if stop == len(words):
                break
            start = max(stop - overlap_words, start + 1)
        return chunks


def build_chunks(
    include_malicious: bool = True,
    profile: str = "default",
    knowledge_dir: Path | None = None,
) -> list[DocumentChunk]:
    excluded = []
    if profile == "gapped":
        excluded = ["xarn_velgor.md", "synth_flux.md", "void_core.md"]

    chunks: list[DocumentChunk] = []
    for path in iter_document_paths(knowledge_dir, include_malicious, excluded):
        title, body = read_title_and_body(path)
        document_text = f"{title}\n\n{body}"
        split_chunks = split_text(document_text, config.DEFAULT_CHUNK_SIZE, config.DEFAULT_CHUNK_OVERLAP)
        for index, text in enumerate(split_chunks):
            if profile == "gapped" and any(term in text.lower() for term in GAP_TERMS):
                continue
            chunk_id = f"{path.stem}:{index}"
            chunks.append(
                DocumentChunk(
                    id=chunk_id,
                    text=text,
                    metadata={
                        "id": chunk_id,
                        "source": str(path.relative_to(config.PROJECT_DIR)),
                        "title": title,
                        "chunk_index": index,
                        "sha256": file_hash(path),
                        "profile": profile,
                        "contains_prompt_injection": has_prompt_injection(text),
                    },
                )
            )
    return chunks
