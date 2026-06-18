from __future__ import annotations

import os
from dataclasses import dataclass


DEFAULT_OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
LOCAL_MODEL_NAME = "local-deterministic-demo"


@dataclass(frozen=True)
class ProviderDecision:
    requested_provider: str
    selected_provider: str
    model: str
    available: bool
    reason: str


def has_openai_key() -> bool:
    value = os.getenv("OPENAI_API_KEY", "").strip()
    return value.startswith("sk-") and len(value) > 20


def provider_status() -> list[dict[str, object]]:
    openai_available = has_openai_key()
    return [
        {
            "provider": "local_mock",
            "available": True,
            "model": LOCAL_MODEL_NAME,
            "reason": "Modo local deterministico disponible sin APIs externas.",
            "requires_api_key": False,
            "exposes_secret_to_frontend": False,
        },
        {
            "provider": "openai_api",
            "available": openai_available,
            "model": DEFAULT_OPENAI_MODEL,
            "reason": (
                "OPENAI_API_KEY detectada en variables de entorno."
                if openai_available
                else "OPENAI_API_KEY no esta configurada; se conserva ejecucion local segura."
            ),
            "requires_api_key": True,
            "exposes_secret_to_frontend": False,
        },
    ]


def select_provider(requested_provider: str) -> ProviderDecision:
    if requested_provider == "openai_api":
        if has_openai_key():
            # This migration exposes provider readiness only. Live calls remain behind a credential-confirmed adapter.
            return ProviderDecision(
                requested_provider=requested_provider,
                selected_provider="openai_api",
                model=DEFAULT_OPENAI_MODEL,
                available=True,
                reason="OpenAI API seleccionada; adaptador live pendiente de habilitacion explicita.",
            )
        return ProviderDecision(
            requested_provider=requested_provider,
            selected_provider="local_mock",
            model=LOCAL_MODEL_NAME,
            available=False,
            reason="OpenAI API solicitada, pero falta OPENAI_API_KEY. Se usa fallback local.",
        )

    return ProviderDecision(
        requested_provider="local_mock",
        selected_provider="local_mock",
        model=LOCAL_MODEL_NAME,
        available=True,
        reason="Proveedor local seleccionado por defecto.",
    )
