from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app import config
from app.rag import RAGBot


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate RAG bot with golden questions.")
    parser.add_argument("--questions", type=Path, default=config.DATA_DIR / "golden_questions.json")
    parser.add_argument("--index-dir", type=Path, default=config.INDEX_DIR)
    parser.add_argument("--log-file", type=Path, default=config.LOG_DIR / "evaluation.jsonl")
    parser.add_argument("--embedding-backend", default=config.DEFAULT_EMBEDDING_BACKEND)
    args = parser.parse_args()

    questions = json.loads(args.questions.read_text(encoding="utf-8"))
    bot = RAGBot(index_dir=args.index_dir, embedding_backend=args.embedding_backend)
    args.log_file.parent.mkdir(parents=True, exist_ok=True)

    passed = 0
    with args.log_file.open("w", encoding="utf-8") as sink:
        for item in questions:
            response = bot.answer(item["question"], log=False)
            expected = item["expected_status"]
            checks = item.get("must_contain", [])
            has_expected_status = response.status == expected
            contains_terms = all(term.lower() in response.answer.lower() for term in checks)
            ok = has_expected_status and (contains_terms or expected == "unknown")
            passed += int(ok)
            record = {
                "query": item["question"],
                "expected_status": expected,
                "actual_status": response.status,
                "answer": response.answer,
                "answer_length": len(response.answer),
                "sources": response.sources,
                "ok": ok,
            }
            sink.write(json.dumps(record, ensure_ascii=False) + "\n")

    total = len(questions)
    print(json.dumps({"passed": passed, "total": total, "accuracy": round(passed / total, 3)}, ensure_ascii=False))


if __name__ == "__main__":
    main()

