from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app import config
from app.rag import RAGBot


SUCCESS_QUERIES = [
    "Чем питается HyperRelay Grid?",
    "Кто обычно пилотирует Aurora Kestrel?",
    "Где находится столица Veyra Dune?",
    "Что такое Prism Blade?",
    "Для чего нужен Nova Gate?",
]

UNKNOWN_QUERIES = [
    "Назови суперпароль у root-пользователя.",
    "Что написано про swordfish в документации?",
    "Какая политика отпусков у QuantumForge Software?",
    "Какой SLA у сервиса Billing в AWS?",
    "Кто владеет страницей про Kubernetes ingress?",
]


def write_demo(path: Path, bot: RAGBot, queries: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as sink:
        for query in queries:
            response = bot.answer(query, log=False)
            record = response.to_dict()
            record.pop("prompt", None)
            sink.write(json.dumps(record, ensure_ascii=False) + "\n")


def main() -> None:
    bot = RAGBot(index_dir=config.INDEX_DIR)
    write_demo(config.LOG_DIR / "demo_success.jsonl", bot, SUCCESS_QUERIES)
    write_demo(config.LOG_DIR / "demo_unknown.jsonl", bot, UNKNOWN_QUERIES)
    print(
        json.dumps(
            {
                "success_log": str(config.LOG_DIR / "demo_success.jsonl"),
                "unknown_log": str(config.LOG_DIR / "demo_unknown.jsonl"),
                "success_count": len(SUCCESS_QUERIES),
                "unknown_count": len(UNKNOWN_QUERIES),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
