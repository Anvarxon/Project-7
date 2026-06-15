from __future__ import annotations

import argparse

from .rag import create_bot_from_env


def main() -> None:
    parser = argparse.ArgumentParser(description="Ask the QuantumForge RAG bot.")
    parser.add_argument("question", nargs="*", help="Question to ask. Starts REPL when omitted.")
    parser.add_argument("--unsafe", action="store_true", help="Disable prompt-injection filtering.")
    args = parser.parse_args()

    bot = create_bot_from_env()
    if args.question:
        response = bot.answer(" ".join(args.question), protection=not args.unsafe)
        print(response.answer)
        return

    print("QuantumForge RAG Bot. Type 'exit' to stop.")
    while True:
        question = input("> ").strip()
        if question.lower() in {"exit", "quit"}:
            break
        if not question:
            continue
        response = bot.answer(question, protection=not args.unsafe)
        print(response.answer)


if __name__ == "__main__":
    main()

