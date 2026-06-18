from __future__ import annotations

from dataclasses import dataclass

from app.tools.token_tools import DEMO_INPUT_TOKEN_PRICE, DEMO_OUTPUT_TOKEN_PRICE


@dataclass(frozen=True)
class LatencySample:
    stage: str
    latency_ms: int


def estimate_local_compute(input_tokens: int, output_tokens: int, context_tokens: int) -> dict[str, object]:
    total_tokens = input_tokens + output_tokens
    latency_ms = 35 + (total_tokens * 3)
    return {
        "provider": "local_mock",
        "model": "local-deterministic-demo",
        "latency_ms": latency_ms,
        "estimated_cpu_ms": 18 + (total_tokens * 2),
        "estimated_ram_mb": 96 + min(256, context_tokens // 2),
        "estimated_context_tokens": context_tokens,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
        "estimated_cost_usd": 0.0,
        "mode_note": "Ejecucion local deterministica; costo monetario externo cero, costo computacional estimado.",
    }


def estimate_openai_compute(model: str, input_tokens: int, output_tokens: int, context_tokens: int) -> dict[str, object]:
    total_tokens = input_tokens + output_tokens
    estimated_cost = (input_tokens * DEMO_INPUT_TOKEN_PRICE) + (output_tokens * DEMO_OUTPUT_TOKEN_PRICE)
    return {
        "provider": "openai_api",
        "model": model,
        "latency_ms": 420 + (total_tokens * 7),
        "estimated_cpu_ms": 0,
        "estimated_ram_mb": 0,
        "estimated_context_tokens": context_tokens,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
        "estimated_cost_usd": round(estimated_cost, 6),
        "mode_note": "Estimacion educativa de servicio cloud; no representa tarifa vigente.",
    }
