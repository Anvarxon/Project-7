# Задание 4-5. Демонстрационные диалоги

Фактические результаты сформированы командой `python scripts/run_demo.py`.

## Успешные ответы

См. `logs/demo_success.jsonl`: 5 записей со статусом `answered`.

Проверенные темы:

- HyperRelay Grid
- Aurora Kestrel
- Veyra Dune
- Prism Blade
- Nova Gate

## Отказы и фильтрация

См. `logs/demo_unknown.jsonl`: 5 записей со статусом `unknown`.

Проверенные сценарии:

- вопрос про root-пароль;
- вопрос про `swordfish`;
- отсутствующая HR-политика;
- отсутствующий SLA сервиса Billing;
- отсутствующий владелец Kubernetes ingress-страницы.
