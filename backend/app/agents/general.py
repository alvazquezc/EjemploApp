from __future__ import annotations

from typing import Any, Optional

from app.agents.base import AgentContext, BaseAgent


class GeneralAgent(BaseAgent):
    name = "GeneralAgent"
    description = "Responde preguntas generales y resume contenido de forma breve."

    def respond(self, context: AgentContext, tool_output: Optional[dict[str, Any]]) -> str:
        intent = context.get("intent", "general_question")
        if intent == "summarize_document":
            return (
                "Resumen educativo: identifique el tema central, reduzca detalles repetidos y conserve los puntos "
                "accionables. En esta demo no se cargan documentos externos; se resume solo el texto enviado."
            )
        if intent == "unknown_intent":
            return "No detecte una intencion clara. Reformula el mensaje con mas contexto para ver una ruta mas especifica."
        token_count = tool_output.get("estimated_tokens") if tool_output else context.get("input_tokens", 0)
        return f"Recibi tu mensaje y lo procese con una ruta general. Estimacion local de entrada: {token_count} tokens."
