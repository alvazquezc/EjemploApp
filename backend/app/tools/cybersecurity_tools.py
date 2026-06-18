from __future__ import annotations

from app.services.security_rules import load_security_rules


def cybersecurity_rule_checker(text: str) -> dict[str, object]:
    normalized = text.lower()
    rules = load_security_rules()
    matched_rule_ids: list[str] = []

    keyword_map = {
        "no_hardcoded_tokens": ["hardcode", "token", "api key", "secret"],
        "environment_variables_for_secrets": ["env", "environment", "variable", "secreto"],
        "strict_input_validation": ["validacion", "input", "entrada"],
        "payload_size_limit": ["payload", "tamano", "size", "limite"],
        "basic_prompt_injection_detection": ["prompt injection", "inyeccion", "jailbreak"],
        "tool_allowlist": ["herramienta", "allowlist", "tool"],
        "least_privilege": ["privilegio", "permiso", "rbac"],
        "max_token_budget": ["presupuesto", "tokens", "costo"],
        "no_log_secrets": ["log", "registro", "secret"],
    }

    for rule in rules:
        keywords = keyword_map.get(rule.id, [])
        if any(keyword in normalized for keyword in keywords):
            matched_rule_ids.append(rule.id)

    return {
        "matched_rules": matched_rule_ids[:8],
        "available_rules": len(rules),
        "recommendation": "Aplica validacion estricta, allowlist de herramientas y minimizacion de contexto.",
    }

