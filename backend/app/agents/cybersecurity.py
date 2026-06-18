from __future__ import annotations

from typing import Any, Optional

from app.agents.base import AgentContext, BaseAgent


class CybersecurityAgent(BaseAgent):
    name = "CybersecurityAgent"
    description = "Da recomendaciones de seguridad para agentes, tokens y herramientas."

    def respond(self, context: AgentContext, tool_output: Optional[dict[str, Any]]) -> str:
        matched = []
        if tool_output:
            matched = list(tool_output.get("matched_rules", []))
        if matched:
            return (
                "La revision local encontro reglas relacionadas: "
                f"{', '.join(matched)}. Prioriza validacion de entradas, minimizacion de contexto y allowlist de herramientas."
            )
        return (
            "Para una app con agentes, aplica secretos en variables de entorno, allowlist de herramientas, presupuesto de "
            "tokens, logs sin secretos y bloqueo fail closed ante errores de politica."
        )
