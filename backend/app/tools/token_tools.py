from __future__ import annotations

from app.services.text_processing import estimate_tokens, tokenize


DEMO_INPUT_TOKEN_PRICE = 0.00000015
DEMO_OUTPUT_TOKEN_PRICE = 0.0000006


def token_counter(text: str) -> dict[str, object]:
    tokens = tokenize(text)
    return {
        "estimated_tokens": estimate_tokens(text),
        "token_count_by_regex": len(tokens),
        "sample_tokens": tokens[:24],
        "estimator": "max(regex_tokens, chars/4)",
    }


def token_cost_estimator(text: str, expected_output_tokens: int = 120) -> dict[str, object]:
    input_tokens = estimate_tokens(text)
    estimated_cost = (input_tokens * DEMO_INPUT_TOKEN_PRICE) + (expected_output_tokens * DEMO_OUTPUT_TOKEN_PRICE)
    return {
        "input_tokens": input_tokens,
        "expected_output_tokens": expected_output_tokens,
        "estimated_total_tokens": input_tokens + expected_output_tokens,
        "estimated_cost_usd": round(estimated_cost, 6),
        "pricing_note": "Precio ilustrativo local; no representa una tarifa real vigente.",
    }

