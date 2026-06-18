# Migration Report

## Diagnostico inicial

### Estado original

El proyecto ya existia como demo funcional de chatbot educativo con:

- Backend FastAPI en `backend/app`.
- Frontend React + Vite + TypeScript en `frontend/src`.
- Visualizacion de flujo con React Flow.
- Pipeline trazado por etapas.
- Detector de intenciones por reglas.
- Refuerzo OpenIA/OpenAI-compatible offline.
- Agentes locales: `GeneralAgent`, `TokenCostAgent`, `CybersecurityAgent`, `CodeAgent`.
- Herramientas locales en allowlist: `token_counter`, `token_cost_estimator`, `cybersecurity_rule_checker`.
- Reglas de seguridad en `backend/security_rules.yaml`.
- Ejemplos defensivos de ataques IA.
- Reporte tecnico en Markdown, LaTeX y PDF.

### Componentes existentes

| Componente | Ruta | Estado |
| --- | --- | --- |
| API FastAPI | `backend/app/main.py` | Operativo |
| Modelos Pydantic | `backend/app/schemas.py` | Operativo, extensible |
| Pipeline | `backend/app/services/pipeline.py` | Operativo, pero procedural |
| Detector de intencion | `backend/app/services/intent_detector.py` | Operativo |
| Refuerzo OpenIA offline | `backend/app/services/openia_intent_reinforcer.py` | Operativo |
| Policy guard | `backend/app/services/policy_guard.py` | Operativo |
| Orquestador | `backend/app/services/orchestrator.py` | Operativo |
| Agentes | `backend/app/agents/` | Operativos |
| Herramientas | `backend/app/tools/` | Operativas |
| Frontend | `frontend/src/` | Operativo |
| Documentacion | `docs/` | Operativa |

### Modulos reutilizables

- `text_processing.py`: normalizacion, tokenizacion, estimacion de tokens y entidades.
- `intent_detector.py`: clasificacion base por reglas.
- `openia_intent_reinforcer.py`: refuerzo semantico local.
- `policy_guard.py`: deteccion basica de prompt injection y limites de tokens.
- `orchestrator.py`: mapeo intencion-agente-herramienta.
- `agents/*`: respuestas deterministas por dominio.
- `tools/*`: herramientas locales puras.
- Componentes React: `ChatPanel`, `FlowPanel`, `MetricBar`, `InspectorPanel`.

### Funcionalidades operativas

- Envio de mensajes desde frontend.
- Procesamiento backend sin APIs externas.
- Trazas estructuradas por etapa.
- Visualizacion animada del pipeline.
- Inspector JSON por nodo.
- Conteo aproximado de tokens.
- Costo estimado ilustrativo.
- Bloqueo de prompt injection.
- Redaccion de secretos en trazas.
- Ejemplos educativos de ataques IA.
- Generacion de PDF de reporte tecnico.

## Deuda tecnica identificada

1. El pipeline esta implementado como una funcion procedural grande.
2. No existe etapa explicita de `provider_selection`.
3. No existe etapa explicita de `prompt_builder`.
4. No existe etapa explicita de `provider_execution`.
5. La comparacion local vs OpenAI no esta modelada como contrato de datos.
6. El frontend muestra metricas resumidas, pero no un dashboard inferior dedicado a tokens y computo.
7. Las reglas de seguridad estan en `backend/security_rules.yaml`; el nuevo prompt maestro solicita `config/security_rules.yaml`.
8. No existe endpoint `GET /api/provider-status`.
9. La arquitectura aun comunica mas un chatbot local que un demostrador moderno de LLMs, tokens, proveedores, costos y observabilidad.
10. No existe interfaz `PipelineNode`; se recomienda introducirla en una fase posterior para evitar una reescritura riesgosa.

## Limitaciones arquitectonicas

- El backend esta acoplado a una sola ruta de ejecucion local.
- La seleccion de proveedor no es un concepto de dominio explicito.
- La construccion de prompt no se expone como artefacto inspeccionable.
- El costo y la latencia no estan centralizados en una capa de observabilidad.
- La integracion real con OpenAI requiere manejo seguro de credenciales antes de agregar llamadas live.

## Plan de migracion incremental

### Etapa 1 - Observabilidad y proveedores sin romper modo local

- Agregar `provider` al request, con default `local_mock`.
- Agregar `GET /api/provider-status`.
- Agregar etapa `provider_selection`.
- Agregar etapa `prompt_builder`.
- Agregar etapa `provider_execution`.
- Mantener `intent_reinforcement` como extension existente.
- Agregar resumen de observabilidad: tokens, costo, latencia, proveedor, modelo, CPU/RAM/contexto estimados.
- Agregar dashboard inferior en frontend.
- Conservar compatibilidad con llamadas existentes que solo envian `message`.

### Etapa 2 - Configuracion y seguridad

- Crear `config/security_rules.yaml` con las reglas ampliadas.
- Hacer que el backend cargue `config/security_rules.yaml` como fuente preferente y mantenga fallback a `backend/security_rules.yaml`.
- Agregar `.env.example` sin secretos reales.

### Etapa 3 - Documentacion de arquitectura

- Crear `docs/software_design.md`.
- Crear `docs/uml.md` con Mermaid valido.
- Actualizar README y reportes con el nuevo flujo.

### Etapa 4 - OpenAI real bajo compuerta de credenciales

- No se implementa llamada live en esta migracion sin confirmacion explicita de manejo de `OPENAI_API_KEY`.
- El sistema queda preparado para integrar el SDK oficial en un adaptador de infraestructura.
- Riesgo principal: exponer secretos o acoplar UI a proveedor externo. Mitigacion: backend-only, variables de entorno, redaccion de logs y fail closed.

## Cambios realizados

### Etapa 1

- Se agrego `provider` opcional al request.
- Se agrego `GET /api/provider-status`.
- Se agrego etapa `provider_selection`.
- Se agrego etapa `prompt_builder`.
- Se agrego etapa `provider_execution`.
- Se agrego `ProviderSummary` y `ComputeMetrics` a la respuesta.
- Se agrego selector de modo en frontend.
- Se agrego dashboard inferior Token & Compute.
- Se conservaron agentes, herramientas y modo local.

### Etapa 2

- Se agrego `config/security_rules.yaml` con reglas ampliadas por categoria.
- El backend ahora usa `config/security_rules.yaml` como fuente preferente y conserva `backend/security_rules.yaml` como fallback.
- Se agrego `.env.example` sin secretos reales.

### Etapa 3

- Se agrego `docs/software_design.md`.
- Se agrego `docs/uml.md` con Mermaid para casos de uso, componentes, clases, secuencias, actividad y despliegue.

## Justificacion tecnica

La migracion se plantea como extension y encapsulamiento porque el sistema actual ya funciona. Reemplazar el pipeline completo por una arquitectura nueva aumentaria riesgo de regresion. La prioridad es introducir conceptos faltantes como proveedor, prompt builder y observabilidad manteniendo la API existente.

## Impacto esperado

- Mayor claridad pedagogica sobre aplicaciones modernas con LLMs.
- Visualizacion explicita de proveedor, prompt, tokens, costos y latencia.
- Compatibilidad con modo local existente.
- Base preparada para una integracion OpenAI real posterior.

## Riesgos

- Aumentar el numero de etapas puede requerir mas espacio visual en React Flow.
- Si se habilita OpenAI real sin compuerta de credenciales, existe riesgo de fuga de secretos.
- La estimacion de tokens/costos sigue siendo aproximada hasta usar un tokenizer/modelo real.

## Compatibilidad

- `POST /api/chat` seguira aceptando `{ "message": "texto" }`.
- El nuevo campo `provider` sera opcional y usara `local_mock` por defecto.
- Los agentes y herramientas existentes se conservan.
- Las reglas existentes se preservan como fallback.

## Validacion posterior a la migracion

Comandos ejecutados:

```bash
cd backend
.venv/bin/python -m compileall -q app
.venv/bin/pip check

cd frontend
npm run build
npm audit --audit-level=moderate
```

Resultados:

- Backend compila sin errores.
- `pip check` reporta `No broken requirements found`.
- Frontend compila TypeScript y Vite sin errores.
- `npm audit --audit-level=moderate` reporta `found 0 vulnerabilities`.
- `GET /api/provider-status` responde con `local_mock` disponible y `openai_api` sin exponer secretos.
- `POST /api/chat` con `provider=local_mock` responde con 15 etapas.
- `POST /api/chat` con `provider=openai_api` sin `OPENAI_API_KEY` aplica fallback seguro a `local_mock`.

## Arquitectura Original vs Arquitectura Reestructurada

| Aspecto | Arquitectura original | Arquitectura reestructurada |
| --- | --- | --- |
| Proveedor | Implicito local | Explicito: `local_mock` u `openai_api` preparado |
| Prompt | No era etapa propia | `prompt_builder` inspeccionable |
| Ejecucion IA | Respuesta local de agente | `provider_execution` separa proveedor de respuesta final |
| Observabilidad | Tokens/costo resumidos | Tokens, costo, latencia, proveedor, modelo, CPU/RAM/contexto |
| Seguridad | Policy guard y YAML backend | Mantiene guard, agrega config ampliada y provider status |
| Frontend | Tres paneles | Tres paneles + dashboard inferior de tokens y computo |
| OpenAI | Refuerzo offline conceptual | Modo OpenAI API representado, sin llamada live hasta credencial |
| Compatibilidad | Chat local funcional | Chat local funcional conservado |
