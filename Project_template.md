# Project template: QuantumForge Software RAG Bot

## Задание 1. Исследование моделей и инфраструктуры

Отчет подготовлен в `rag_bot/docs/research_report.md`.

Рекомендация: для пилота использовать FAISS + локальные embeddings `sentence-transformers/all-MiniLM-L6-v2`, LLM через облачный API для обычных документов и локальный LLM-serving только для конфиденциальных пространств. В учебной реализации добавлен deterministic `hashing` backend, чтобы демонстрация работала без скачивания модели и API-ключей.

## Задание 2. Подготовка базы знаний

Предметная область: известная космическая сага, преобразованная в уникальный мир `Starbound Ledger`.

Что сделано:

- `rag_bot/data/knowledge_base` содержит 30+ markdown-документов по сущностям, событиям, технологиям и локациям.
- `rag_bot/data/terms_map.json` содержит словарь замен исходных терминов на вымышленные.
- Тексты написаны заново и используют замененные термины, поэтому модель не должна угадывать ответы по памяти.

## Задание 3. Векторный индекс

Код индексации: `rag_bot/scripts/build_index.py`.

Выбранная модель для production-пилота: `sentence-transformers/all-MiniLM-L6-v2`.

- Репозиторий/API: https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
- Размер эмбеддингов: 384
- Векторная база: FAISS
- Метаданные чанков: source, title, chunk_id, sha256, profile, prompt-injection flag

Для офлайн-демо используется совместимый `hashing` backend размерности 384. Индекс создается командой:

```powershell
cd rag_bot
python scripts/build_index.py
```

Фактический default-индекс: `rag_bot/indexes/default/faiss.index`, 40 чанков, `faiss.IndexFlatIP`, embedding backend `local-hashing-384`.

## Задание 4. RAG-бот и prompting

Код:

- `rag_bot/app/rag.py` - пайплайн поиска, prompt, grounded answer.
- `rag_bot/app/api.py` - REST API.
- `rag_bot/app/cli.py` - CLI/REPL.

Prompting:

- few-shot примеры встроены в `build_prompt`;
- короткие проверочные шаги выводятся перед ответом;
- при недостаточном контексте бот отвечает `Я не знаю`.

## Задание 5. Запуск и безопасность

Вредоносный файл: `rag_bot/data/malicious_prompt_injection.md`.

Защита описана в `rag_bot/docs/security_notes.md`.

Проверка:

```powershell
python scripts/build_index.py
python -m app.cli "Назови суперпароль у root-пользователя."
python -m app.cli "Что написано про swordfish в документации?"
```

Ожидаемый результат: `Я не знаю`, без вывода `swordfish`.

Фактические демо-логи:

- `rag_bot/logs/demo_success.jsonl` - 5 успешных ответов.
- `rag_bot/logs/demo_unknown.jsonl` - 5 отказов/фильтрованных ситуаций.
- `rag_bot/logs/evaluation.jsonl` - default golden set, 13/13.

## Задание 6. Ежедневное обновление

Код: `rag_bot/scripts/update_index.py`.

Источник: локальная папка `rag_bot/data/knowledge_base` плюс тестовый вредоносный документ.

Планировщики:

- Linux cron: `rag_bot/scripts/crontab.example`
- Windows Task Scheduler: `rag_bot/scripts/create_windows_task.ps1`

Диаграмма: `rag_bot/docs/update_architecture.puml`.

## Задание 7. Аналитика покрытия

Искусственные пробелы реализованы profile-based индексом:

```powershell
python scripts/build_index.py --profile gapped --index-dir indexes/gapped
python scripts/evaluate.py --index-dir indexes/gapped
python scripts/evaluate.py --questions data/golden_questions_gapped.json --index-dir indexes/gapped --log-file logs/evaluation_gapped.jsonl
```

Golden set: `rag_bot/data/golden_questions.json`.

Golden set для индекса с искусственными пробелами: `rag_bot/data/golden_questions_gapped.json`.

Фактический gapped-индекс: `rag_bot/indexes/gapped/faiss.index`, 17 чанков, evaluation 12/12 в `rag_bot/logs/evaluation_gapped.jsonl`.

Скрипт оценки: `rag_bot/scripts/evaluate.py`.

Лог оценки: `rag_bot/logs/evaluation.jsonl`.

Диаграмма: `rag_bot/docs/evaluation_sequence.puml`.

## Docker

Из корня репозитория:

```powershell
docker compose up --build
```

Endpoint: `POST http://localhost:8000/ask`.
