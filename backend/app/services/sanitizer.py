from __future__ import annotations

import re
from typing import Any


SECRET_PATTERNS = [
    re.compile(r"\bsk-[A-Za-z0-9_\-]{12,}\b"),
    re.compile(r"\b(?:api[_-]?key|token|secret|password)\s*[:=]\s*['\"]?[^'\"\s]{6,}", re.IGNORECASE),
    re.compile(r"\b[A-Za-z0-9_\-]{24,}\.[A-Za-z0-9_\-]{24,}\.[A-Za-z0-9_\-]{24,}\b"),
]


def sanitize_text(value: str) -> str:
    sanitized = value
    for pattern in SECRET_PATTERNS:
        sanitized = pattern.sub("[REDACTED_SECRET]", sanitized)
    return sanitized


def safe_preview(value: str, limit: int = 160) -> str:
    sanitized = sanitize_text(value)
    if len(sanitized) <= limit:
        return sanitized
    return f"{sanitized[:limit]}..."


def sanitize_payload(value: Any) -> Any:
    if isinstance(value, str):
        return sanitize_text(value)
    if isinstance(value, list):
        return [sanitize_payload(item) for item in value]
    if isinstance(value, tuple):
        return tuple(sanitize_payload(item) for item in value)
    if isinstance(value, dict):
        return {str(key): sanitize_payload(item) for key, item in value.items()}
    return value


def contains_secret_like_text(value: str) -> bool:
    return any(pattern.search(value) for pattern in SECRET_PATTERNS)

