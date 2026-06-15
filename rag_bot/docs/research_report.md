# Задание 1. Исследование моделей и инфраструктуры

Дата проверки внешних источников: 2026-06-15.

## Контекст задачи

QuantumForge Software нужна внутренняя RAG-система для разработчиков, поддержки, менеджеров, аналитиков и новых сотрудников. Основные требования: быстрый поиск, персонализированные ответы с источниками, выявление пробелов, защита от устаревших или вредоносных документов, масштабирование на десятки тысяч файлов.

## Сравнение LLM

| Вариант | Качество | Скорость | Стоимость | Развертывание | Ограничения |
|---|---|---|---|---|---|
| Локальные Hugging Face модели, например Llama/Mistral/Qwen 7B-14B | Хорошее для простых QA, хуже на сложных корпоративных формулировках без дообучения | Зависит от GPU; CPU слишком медленно | CAPEX/OPEX на GPU, администрирование | Сложнее: GPU, quantization, serving, мониторинг | Лучший контроль данных, но выше DevOps-нагрузка |
| OpenAI GPT-5.4 mini / GPT-5.4 | Высокое качество, хорошие инструкции, стабильный формат | Обычно низкая latency без своего GPU | По официальному прайсу OpenAI GPT-5.4 mini: $0.75 input и $4.50 output за 1M токенов; GPT-5.4: $2.50 input и $15 output за 1M токенов | Самое простое API-внедрение | Данные уходят во внешний API, нужен DPA и контроль регионов |
| YandexGPT Pro/Lite | Хорошее качество на русском, проще юридически для части рынков СНГ | API, без своего GPU | По AI Studio pricing YandexGPT Pro 5.1: $0.006557376 за 1K input и output tokens; Lite дешевле | API-внедрение среднее | Для финско-эстонской компании надо отдельно оценить compliance и доступность регионов |

Рекомендация: для пилота использовать облачную LLM с сильными инструкциями и строгим RAG-контекстом, а для конфиденциальных пространств оставить вариант локального LLM-serving. В учебном проекте генерация сделана локально-экстрактивной, чтобы демо работало без API-ключа.

## Сравнение эмбеддингов

| Вариант | Скорость индексации | Качество поиска | Стоимость | Вывод |
|---|---:|---|---|---|
| Sentence-Transformers `all-MiniLM-L6-v2` | Быстро на CPU, очень быстро на GPU | Хорошее baseline-качество для semantic search, 384-мерные векторы | Бесплатно по API, платим только за CPU/GPU | Лучший выбор для локального пилота и конфиденциальных документов |
| OpenAI `text-embedding-3-small` | Очень быстро через API, batch дешевле | Выше качество и мультиязычность, 1536 измерений | OpenAI docs указывают оплату по input tokens; модель имеет 1536 измерений | Хорошо для production, если разрешен внешний API |
| Yandex Embeddings | API, быстро | Хорошо для русского | По AI Studio: $0.0000827869 за 1K tokens vectorization | Опция для русскоязычных документов, но нужен vendor lock-in анализ |

Выбор для проекта: `all-MiniLM-L6-v2` как рекомендуемая production-конфигурация пилота. В коде также есть `hashing` backend для полностью офлайн-демо без скачивания модели.

## FAISS vs ChromaDB

| Критерий | FAISS | ChromaDB |
|---|---|---|
| Скорость поиска | Очень высокая, библиотека для dense vector similarity search, есть GPU | Достаточно высокая, но больше overhead как БД/сервер |
| Индексация | Простая, быстрый in-memory index, можно сохранить на диск | Удобная ingestion-модель, хранение документов и metadata из коробки |
| Поддержка metadata | Нужно хранить отдельно | Встроенные metadata filters, document storage, dense/sparse/hybrid search |
| Эксплуатация | Минимальная для пилота, но нет полноценного multi-user DB layer | Удобнее для production-команды и фильтров доступа |
| Стоимость | Низкая: CPU/RAM + диск | Низкая self-hosted, выше при Chroma Cloud |

Выбор для учебного проекта: FAISS. Причины: минимальная инфраструктура, высокая скорость, проще Docker-демо, достаточно для 18k markdown и 3k Confluence страниц на пилоте. Для enterprise-версии с ACL, metadata filters и несколькими индексами стоит рассмотреть ChromaDB или Qdrant.

## Рекомендуемые серверные конфигурации

| Вариант | CPU/RAM/GPU | Для чего | Плюсы | Минусы |
|---|---|---|---|---|
| Pilot local | 4 vCPU, 16 GB RAM, без GPU | До 100k чанков, FAISS + локальные embeddings | Дешево, быстро запустить | LLM лучше вызывать облачно |
| Production API | 8 vCPU, 32 GB RAM, без GPU | FAISS/Chroma + OpenAI/Yandex LLM API | Простая эксплуатация, хорошее качество | Данные уходят во внешний API |
| Confidential local | 16 vCPU, 64 GB RAM, 1 GPU 24 GB VRAM | Локальная LLM 7B-14B + локальные embeddings | Контроль данных | Дороже и сложнее поддерживать |
| Scale-out | 16+ vCPU, 64+ GB RAM, managed vector DB, autoscaling API | Много команд, ACL, audit logs | Масштабируемо | Дольше внедрять |

Итоговая рекомендация для QuantumForge: начать с `Production API`: FAISS или ChromaDB, локальные `all-MiniLM-L6-v2` embeddings для конфиденциальных данных, облачная LLM для обычных пространств, строгие ACL и логирование запросов. Через 2-3 месяца сравнить retrieval metrics и стоимость, затем решить, нужен ли локальный LLM-serving для SOC 2 sensitive-документов.

## Источники

- OpenAI pricing: https://developers.openai.com/api/docs/pricing
- OpenAI embeddings guide: https://developers.openai.com/api/docs/guides/embeddings
- Yandex AI Studio pricing: https://aistudio.yandex.ru/docs/en/ai-studio/pricing.html
- Hugging Face all-MiniLM-L6-v2: https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
- FAISS documentation: https://faiss.ai/index.html
- Chroma documentation: https://docs.trychroma.com/docs/overview/introduction

