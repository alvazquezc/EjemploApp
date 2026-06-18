from __future__ import annotations

from typing import Any, Optional

from app.agents.base import AgentContext, BaseAgent


class CodeAgent(BaseAgent):
    name = "CodeAgent"
    description = "Genera orientacion de codigo sin ejecutar contenido del usuario."

    def respond(self, context: AgentContext, tool_output: Optional[dict[str, Any]]) -> str:
        token_count = tool_output.get("estimated_tokens") if tool_output else context.get("input_tokens", 0)
        return (
            "Puedo generar ejemplos de codigo de forma estatica, pero esta demo no ejecuta codigo arbitrario. "
            f"Tu solicitud se analizo como entrada de {token_count} tokens estimados."
        )
