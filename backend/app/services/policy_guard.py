from __future__ import annotations

import re
from dataclasses import dataclass, field

from app.services.sanitizer import contains_secret_like_text


MAX_INPUT_TOKENS = 220

PROMPT_INJECTION_PATTERNS = [
    re.compile(r"ignore (all )?(previous|prior) instructions", re.IGNORECASE),
    re.compile(r"ignora (todas )?(las )?instrucciones", re.IGNORECASE),
    re.compile(r"revela (el )?(prompt|mensaje) (del sistema|interno)", re.IGNORECASE),
    re.compile(r"show (me )?(the )?(system|developer) prompt", re.IGNORECASE),
    re.compile(r"bypass|jailbreak|modo desarrollador", re.IGNORECASE),
    re.compile(r"actua como sistema|act as system", re.IGNORECASE),
]


@dataclass
class PolicyDecision:
    allowed: bool
    triggered_rules: list[str] = field(default_factory=list)
    reason: str = "Mensaje permitido por las reglas locales."


def evaluate_policy(raw_message: str, estimated_tokens: int) -> PolicyDecision:
    triggered_rules: list[str] = []

    if estimated_tokens > MAX_INPUT_TOKENS:
        triggered_rules.append("max_token_budget")

    if contains_secret_like_text(raw_message):
        triggered_rules.append("no_log_secrets")

    for pattern in PROMPT_INJECTION_PATTERNS:
        if pattern.search(raw_message):
            triggered_rules.append("basic_prompt_injection_detection")
            break

    blocking_rules = {"max_token_budget", "basic_prompt_injection_detection", "no_log_secrets"}
    blocked = any(rule_id in blocking_rules for rule_id in triggered_rules)

    if blocked:
        return PolicyDecision(
            allowed=False,
            triggered_rules=triggered_rules,
            reason="La politica local bloqueo el mensaje para evitar fuga de secretos, exceso de presupuesto o prompt injection.",
        )

    return PolicyDecision(allowed=True, triggered_rules=triggered_rules)

