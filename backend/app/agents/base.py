from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Optional


class AgentContext(dict):
    """Simple typed alias for agent inputs."""


class BaseAgent(ABC):
    name: str
    description: str

    @abstractmethod
    def respond(self, context: AgentContext, tool_output: Optional[dict[str, Any]]) -> str:
        raise NotImplementedError
