from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class OrchestrationPlan:
    intent: str
    agent_name: str
    tool_name: Optional[str]
    rationale: str


INTENT_TO_AGENT: dict[str, str] = {
    "explain_tokens": "TokenCostAgent",
    "estimate_token_cost": "TokenCostAgent",
    "summarize_document": "GeneralAgent",
    "generate_code": "CodeAgent",
    "cybersecurity_question": "CybersecurityAgent",
    "general_question": "GeneralAgent",
    "unknown_intent": "GeneralAgent",
}

INTENT_TO_TOOL: dict[str, Optional[str]] = {
    "explain_tokens": "token_counter",
    "estimate_token_cost": "token_cost_estimator",
    "summarize_document": "token_counter",
    "generate_code": "token_counter",
    "cybersecurity_question": "cybersecurity_rule_checker",
    "general_question": "token_counter",
    "unknown_intent": None,
}


def create_plan(intent: str) -> OrchestrationPlan:
    agent_name = INTENT_TO_AGENT.get(intent, "GeneralAgent")
    tool_name = INTENT_TO_TOOL.get(intent)
    rationale = f"Intent '{intent}' routed to {agent_name}"
    if tool_name:
        rationale += f" with tool '{tool_name}'"
    return OrchestrationPlan(intent=intent, agent_name=agent_name, tool_name=tool_name, rationale=rationale)
