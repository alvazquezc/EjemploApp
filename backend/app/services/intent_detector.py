from __future__ import annotations

from dataclasses import dataclass


IntentName = str


@dataclass(frozen=True)
class IntentResult:
    intent: IntentName
    confidence: float
    matched_keywords: list[str]


INTENT_KEYWORDS: dict[str, list[str]] = {
    "explain_tokens": [
        "explica token",
        "explica tokens",
        "explicame token",
        "que es token",
        "que son los tokens",
        "que son tokens",
        "como funcionan los tokens",
        "tokenizacion",
    ],
    "estimate_token_cost": [
        "costo",
        "coste",
        "precio",
        "cuanto cuesta",
        "estimar tokens",
        "presupuesto",
    ],
    "summarize_document": [
        "resume",
        "resumen",
        "resumir",
        "sintetiza",
        "documento",
        "articulo",
    ],
    "generate_code": [
        "codigo",
        "code",
        "programa",
        "funcion",
        "script",
        "react",
        "python",
        "typescript",
    ],
    "cybersecurity_question": [
        "ciberseguridad",
        "seguridad",
        "prompt injection",
        "inyeccion",
        "secretos",
        "api key",
        "hardcode",
        "owasp",
        "tls",
    ],
}


def detect_intent(normalized_text: str) -> IntentResult:
    matches: list[tuple[str, list[str]]] = []
    for intent, keywords in INTENT_KEYWORDS.items():
        matched = [keyword for keyword in keywords if keyword in normalized_text]
        if matched:
            matches.append((intent, matched))

    if matches:
        intent, matched_keywords = max(matches, key=lambda item: len(item[1]))
        confidence = min(0.95, 0.45 + (0.15 * len(matched_keywords)))
        return IntentResult(intent=intent, confidence=confidence, matched_keywords=matched_keywords)

    if len(normalized_text.split()) <= 2:
        return IntentResult(intent="unknown_intent", confidence=0.2, matched_keywords=[])

    return IntentResult(intent="general_question", confidence=0.55, matched_keywords=[])
