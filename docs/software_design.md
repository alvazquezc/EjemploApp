# Software Design

## Objetivo

El sistema es un demostrador educativo de aplicaciones modernas basadas en LLMs. No busca ser solamente un chatbot, sino un inspector de flujo que muestra como se procesan mensajes, tokens, intenciones, prompts, proveedores, agentes, herramientas, costos, latencia, seguridad y auditoria.

## Alcance

La reestructuracion conserva el modo local existente y agrega una arquitectura explicita de proveedores:

- `local_mock`: ejecucion deterministica local, sin APIs externas.
- `openai_api`: modo representado y observable para explicar consumo cloud; la llamada live queda pendiente de compuerta segura de credenciales.

## Arquitectura por capas

| Capa | Implementacion | Responsabilidad |
| --- | --- | --- |
| Presentation | `frontend/src` | Chat, selector de proveedor, React Flow, inspector y dashboard token/compute |
| Application | `backend/app/services/pipeline.py` | Orquestacion del caso de uso `/api/chat` |
| Domain | `agents`, `orchestrator`, `intent_detector`, `tools` | Intenciones, agentes, herramientas y reglas de negocio |
| Infrastructure | `provider_selection`, config YAML, endpoints FastAPI | Estado de proveedores, configuracion, API HTTP |

## Backend

El backend expone:

- `GET /api/health`
- `GET /api/security-rules`
- `GET /api/provider-status`
- `GET /api/ai-attack-examples`
- `POST /api/chat`

`POST /api/chat` acepta:

```json
{
  "message": "texto",
  "provider": "local_mock"
}
```

`provider` es opcional y usa `local_mock` por defecto para conservar compatibilidad.

## Pipeline

El pipeline actual contiene 15 etapas. Incluye las 14 etapas solicitadas por el prompt maestro y conserva `intent_reinforcement` como extension funcional existente:

1. `raw_input`
2. `normalization`
3. `tokenization`
4. `entity_extraction`
5. `intent_detection`
6. `intent_reinforcement`
7. `policy_guard`
8. `provider_selection`
9. `orchestrator`
10. `prompt_builder`
11. `agent_selection`
12. `tool_execution`
13. `provider_execution`
14. `response_generation`
15. `audit_log`

## OpenAI API

El sistema diferencia claramente entre:

- arquitectura preparada para OpenAI API;
- ejecucion local deterministica;
- fallback seguro cuando no existe `OPENAI_API_KEY`.

El backend nunca expone claves al frontend. `GET /api/provider-status` reporta disponibilidad sin revelar secretos.

La llamada real al SDK oficial de OpenAI no se habilita en esta migracion porque requiere confirmacion explicita de manejo de credenciales. Esta decision evita acoplar la demo a una clave local y mantiene la compatibilidad offline.

## Modo local

El modo local muestra:

- tokens estimados;
- contexto estimado;
- CPU estimada;
- RAM estimada;
- latencia estimada;
- costo externo igual a cero;
- respuesta generada por agentes deterministas.

## Prompt Builder

La etapa `prompt_builder` expone:

- `system_prompt`;
- `developer_policy`;
- `conversation_history`;
- `retrieved_context`;
- `tool_results`;
- `user_message`;
- `final_prompt_preview`;
- `estimated_input_tokens`.

El objetivo es mostrar como una aplicacion LLM moderna arma el prompt antes de llamar a un proveedor.

## Observabilidad

La respuesta incluye:

- `token_usage`;
- `provider`;
- `compute`;
- `security`;
- `intent_reinforcement`;
- `trace`.

El frontend renderiza esta informacion en:

- Metric bar superior;
- React Flow central;
- Inspector JSON;
- Dashboard inferior Token & Compute.

## Seguridad

Controles actuales:

- validacion Pydantic;
- rechazo de mensajes vacios;
- limite de longitud;
- deteccion basica de prompt injection;
- redaccion de secretos en trazas;
- allowlist de herramientas;
- fallback local si OpenAI API no esta disponible;
- no ejecucion de codigo arbitrario;
- no endpoints destructivos.

## Riesgos

| Riesgo | Mitigacion |
| --- | --- |
| Confundir simulacion con llamada real OpenAI | `provider_execution` indica `executed_live_call=false` |
| Exposicion de API key | Backend-only, status sin secretos, `.env.example` sin valores |
| Crecimiento del pipeline | Mantener trazas uniformes y migrar a `PipelineNode` en etapa futura |
| Estimaciones inexactas | Documentar que tokens/costos son educativos |

## Extensiones

- Implementar adaptador real OpenAI con SDK oficial y credenciales confirmadas.
- Convertir etapas a clases `PipelineNode`.
- Persistir auditoria redacted.
- Agregar tests unitarios por etapa.
- Agregar comparativa historica de latencia/costo.

