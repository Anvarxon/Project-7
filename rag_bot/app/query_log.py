from __future__ import annotations

import json
import time
from pathlib import Path

from . import config


def append_query_log(record: dict, log_path: Path | None = None) -> None:
    target = log_path or config.LOG_DIR / "queries.jsonl"
    target.parent.mkdir(parents=True, exist_ok=True)
    enriched = {"timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), **record}
    with target.open("a", encoding="utf-8") as sink:
        sink.write(json.dumps(enriched, ensure_ascii=False) + "\n")

