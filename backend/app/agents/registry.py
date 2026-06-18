from __future__ import annotations

from app.agents.base import BaseAgent
from app.agents.code import CodeAgent
from app.agents.cybersecurity import CybersecurityAgent
from app.agents.general import GeneralAgent
from app.agents.token_cost import TokenCostAgent


AGENTS: dict[str, BaseAgent] = {
    "GeneralAgent": GeneralAgent(),
    "TokenCostAgent": TokenCostAgent(),
    "CybersecurityAgent": CybersecurityAgent(),
    "CodeAgent": CodeAgent(),
}


def get_agent(name: str) -> BaseAgent:
    try:
        return AGENTS[name]
    except KeyError as exc:
        raise ValueError(f"Agente no registrado: {name}") from exc


def list_agents() -> list[str]:
    return sorted(AGENTS.keys())

