from __future__ import annotations

import os
from pathlib import Path


PACKAGE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = PACKAGE_DIR.parent
DATA_DIR = Path(os.getenv("QF_DATA_DIR", PROJECT_DIR / "data"))
KNOWLEDGE_DIR = Path(os.getenv("QF_KNOWLEDGE_DIR", DATA_DIR / "knowledge_base"))
MALICIOUS_FILE = Path(os.getenv("QF_MALICIOUS_FILE", DATA_DIR / "malicious_prompt_injection.md"))
INDEX_DIR = Path(os.getenv("QF_INDEX_DIR", PROJECT_DIR / "indexes" / "default"))
LOG_DIR = Path(os.getenv("QF_LOG_DIR", PROJECT_DIR / "logs"))

DEFAULT_EMBEDDING_BACKEND = os.getenv("QF_EMBEDDING_BACKEND", "hashing")
DEFAULT_EMBEDDING_MODEL = os.getenv("QF_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
DEFAULT_EMBEDDING_DIM = int(os.getenv("QF_EMBEDDING_DIM", "384"))
DEFAULT_CHUNK_SIZE = int(os.getenv("QF_CHUNK_SIZE", "1200"))
DEFAULT_CHUNK_OVERLAP = int(os.getenv("QF_CHUNK_OVERLAP", "160"))
DEFAULT_TOP_K = int(os.getenv("QF_TOP_K", "5"))
DEFAULT_MIN_SCORE = float(os.getenv("QF_MIN_SCORE", "0.16"))

