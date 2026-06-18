from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any

from app.services.intent_detector import IntentResult


@dataclass(frozen=True)
class IntentReinforcementResult:
    enabled: bool
    provider: str
    original_intent: str
    final_intent: str
    confidence: float
    signals: list[str] = field(default_factory=list)
    rationale: str = ""

    @property
    def changed(self) -> bool:
        return self.original_intent != self.final_intent


OPENIA_SIGNAL_MAP: dict[str, dict[str, list[str]]] = {
    "explain_tokens": {
        "strong": ["que son los tokens", "explica tokens", "tokenizacion", "como funcionan los tokens"],
        "weak": ["tokens", "token"],
    },
    "estimate_token_cost": {
        "strong": ["costo de tokens", "estima el costo", "cuanto cuesta", "presupuesto de tokens"],
        "weak": ["costo", "precio", "presupuesto"],
    },
    "summarize_document": {
        "strong": ["resume este documento", "resumir documento", "haz un resumen"],
        "weak": ["resume", "resumen", "documento"],
    },
    "generate_code": {
        "strong": ["genera codigo", "escribe una funcion", "crea un script", "implementa"],
        "weak": ["codigo", "python", "react", "typescript", "funcion"],
    },
    "cybersecurity_question": {
        "strong": ["prompt injection", "inyeccion de prompt", "hardcoded tokens", "secretos en logs"],
        "weak": ["seguridad", "ciberseguridad", "secretos", "tls", "rbac"],
    },
}


def _mode() -> str:
    return os.getenv("OPENIA_INTENT_REINFORCEMENT_MODE", "offline").strip().lower()


def _score_intents(normalized_text: str, entities: list[dict[str, Any]]) -> tuple[str | None, float, list[str]]:
    entity_values = " ".join(str(entity.get("value", "")) for entity in entities).lower()
    combined_text = f"{normalized_text} {entity_values}"
    scored: list[tuple[str, float, list[str]]] = []

    for intent, signal_groups in OPENIA_SIGNAL_MAP.items():
        signals: list[str] = []
        score = 0.0
        for phrase in signal_groups["strong"]:
            if phrase in combined_text:
                score += 0.35
                signals.append(f"strong:{phrase}")
        for phrase in signal_groups["weak"]:
            if phrase in combined_text:
                score += 0.12
                signals.append(f"weak:{phrase}")
        if signals:
            scored.append((intent, min(score, 0.98), signals))

    if not scored:
        return None, 0.0, []

    best_intent, confidence, signals = max(scored, key=lambda item: item[1])
    return best_intent, confidence, signals[:8]


def reinforce_intent(
    normalized_text: str,
    entities: list[dict[str, Any]],
    base_intent: IntentResult,
) -> IntentReinforcementResult:
    mode = _mode()
    provider = "openia-compatible-offline"

    if mode == "disabled":
        return IntentReinforcementResult(
            enabled=False,
            provider=provider,
            original_intent=base_intent.intent,
            final_intent=base_intent.intent,
            confidence=base_intent.confidence,
            signals=[],
            rationale="Intent reinforcement disabled by OPENIA_INTENT_REINFORCEMENT_MODE.",
        )

    if mode not in {"offline", "local"}:
        return IntentReinforcementResult(
            enabled=False,
            provider=provider,
            original_intent=base_intent.intent,
            final_intent=base_intent.intent,
            confidence=base_intent.confidence,
            signals=[],
            rationale="External OpenAI/OpenIA calls are not enabled in this offline demo.",
        )

    reinforced_intent, reinforced_confidence, signals = _score_intents(normalized_text, entities)
    if not reinforced_intent:
        return IntentReinforcementResult(
            enabled=True,
            provider=provider,
            original_intent=base_intent.intent,
            final_intent=base_intent.intent,
            confidence=base_intent.confidence,
            signals=[],
            rationale="No additional semantic signals found; base intent kept.",
        )

    should_override = base_intent.intent in {"unknown_intent", "general_question"} and reinforced_confidence >= 0.24
    should_strengthen_same = reinforced_intent == base_intent.intent

    final_intent = reinforced_intent if should_override else base_intent.intent
    confidence = max(base_intent.confidence, reinforced_confidence) if should_strengthen_same or should_override else base_intent.confidence
    rationale = (
        "Offline OpenIA-compatible reinforcement selected a more specific intent."
        if should_override
        else "Base detector kept because reinforcement did not exceed override policy."
    )

    return IntentReinforcementResult(
        enabled=True,
        provider=provider,
        original_intent=base_intent.intent,
        final_intent=final_intent,
        confidence=round(confidence, 3),
        signals=signals,
        rationale=rationale,
    )

