from __future__ import annotations

from typing import Any, Optional

from app.agents.base import AgentContext, BaseAgent


class TokenCostAgent(BaseAgent):
    name = "TokenCostAgent"
    description = "Explica tokenizacion y costos estimados con calculos locales."

    def respond(self, context: AgentContext, tool_output: Optional[dict[str, Any]]) -> str:
        intent = context.get("intent")
        if intent == "estimate_token_cost" and tool_output:
            input_tokens = tool_output.get("input_tokens", context.get("input_tokens", 0))
            total_tokens = tool_output.get("estimated_total_tokens", input_tokens)
            cost = tool_output.get("estimated_cost_usd", 0)
            return (
                f"Estimacion local: {input_tokens} tokens de entrada y {total_tokens} tokens totales esperados. "
                f"Costo ilustrativo aproximado: ${cost} USD."
            )

        estimated = tool_output.get("estimated_tokens") if tool_output else context.get("input_tokens", 0)
        return (
            f"Un token es una unidad de texto usada por el modelo. Esta demo estima {estimated} tokens con una regla "
            "simple basada en palabras, signos y longitud del texto."
        )
