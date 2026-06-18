from __future__ import annotations

import re
from collections import Counter
from typing import Any


TOKEN_PATTERN = re.compile(r"\w+|[^\w\s]", re.UNICODE)
URL_PATTERN = re.compile(r"https?://[^\s]+", re.IGNORECASE)
EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")

TECH_KEYWORDS = {
    "api",
    "agent",
    "agente",
    "backend",
    "chatbot",
    "codigo",
    "code",
    "fastapi",
    "frontend",
    "ia",
    "llm",
    "prompt",
    "python",
    "react",
    "token",
    "tokens",
    "typescript",
}


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip()).lower()


def tokenize(text: str) -> list[str]:
    return TOKEN_PATTERN.findall(text)


def estimate_tokens(text: str) -> int:
    word_like_tokens = tokenize(text)
    char_estimate = max(1, round(len(text) / 4))
    return max(len(word_like_tokens), char_estimate)


def extract_entities(text: str) -> list[dict[str, Any]]:
    entities: list[dict[str, Any]] = []
    for url in URL_PATTERN.findall(text):
        entities.append({"type": "url", "value": url})
    for email in EMAIL_PATTERN.findall(text):
        entities.append({"type": "email", "value": email})

    normalized = normalize_text(text)
    tokens = set(tokenize(normalized))
    for keyword in sorted(tokens.intersection(TECH_KEYWORDS)):
        entities.append({"type": "technology_keyword", "value": keyword})

    repeated = [
        {"value": token, "count": count}
        for token, count in Counter(tokenize(normalized)).items()
        if count >= 3 and len(token) > 2
    ]
    if repeated:
        entities.append({"type": "repeated_terms", "value": repeated})

    return entities

