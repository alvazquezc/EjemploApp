from __future__ import annotations

from typing import Any, Callable, Dict

from app.tools.cybersecurity_tools import cybersecurity_rule_checker
from app.tools.token_tools import token_cost_estimator, token_counter


ToolFunction = Callable[..., Dict[str, Any]]

TOOL_ALLOWLIST: dict[str, ToolFunction] = {
    "token_counter": token_counter,
    "token_cost_estimator": token_cost_estimator,
    "cybersecurity_rule_checker": cybersecurity_rule_checker,
}


def execute_tool(name: str, text: str) -> dict[str, Any]:
    tool = TOOL_ALLOWLIST.get(name)
    if tool is None:
        raise ValueError(f"La herramienta '{name}' no esta registrada en la allowlist.")
    return tool(text)


def list_allowed_tools() -> list[str]:
    return sorted(TOOL_ALLOWLIST.keys())
