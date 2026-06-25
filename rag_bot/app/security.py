from __future__ import annotations

import re


PROMPT_INJECTION_PATTERNS = [
    re.compile(r"ignore\s+all\s+instructions", re.IGNORECASE),
    re.compile(r"output\s*:", re.IGNORECASE),
    re.compile(r"system\s+message", re.IGNORECASE),
    re.compile(r"developer\s+message", re.IGNORECASE),
    re.compile(r"root\s*:\s*swordfish", re.IGNORECASE),
    re.compile(r"superpassword|суперпароль|swordfish", re.IGNORECASE),
]


def has_prompt_injection(text: str) -> bool:
    return any(pattern.search(text) for pattern in PROMPT_INJECTION_PATTERNS)


def sanitize_document_text(text: str) -> str:
    safe_lines: list[str] = []
    for line in text.splitlines():
        if has_prompt_injection(line):
            continue
        safe_lines.append(line)
    return "\n".join(safe_lines).strip()


def filter_unsafe_results(results, enabled: bool = True):
    if not enabled:
        return results
    filtered = []
    for result in results:
        if result.metadata.get("contains_prompt_injection") or has_prompt_injection(result.text):
            continue
        filtered.append(result)
    return filtered

