# Chatbot Flow Demo

Demo web educativa de un chatbot con agente orquestador, detector de intenciones, reglas de ciberseguridad y visualizacion interna del flujo de tokens. Funciona localmente sin APIs externas y no requiere claves reales.

## Estructura

```text
backend/
  app/
    agents/          Agentes deterministas por intencion
    services/        Pipeline, politicas, orquestador, reglas e intenciones
    tools/           Herramientas locales registradas en allowlist
    main.py          Endpoints FastAPI
    schemas.py       Modelos Pydantic
  security_rules.yaml
  requirements.txt
frontend/
  src/
    components/      Chat, metricas, flujo React Flow e inspector
    services/        Cliente HTTP
    styles/          CSS de la interfaz
    types/           Tipos TypeScript de la API
```

## Instalacion

Backend:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Frontend:

```bash
cd frontend
npm install
```

## Ejecucion

Backend:

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

Frontend:

```bash
cd frontend
npm run dev
```

Abrir `http://localhost:5173`.

## API

- `GET /api/health`: estado del servicio.
- `GET /api/security-rules`: reglas cargadas desde `backend/security_rules.yaml`.
- `GET /api/provider-status`: disponibilidad de `local_mock` y estado seguro de `openai_api` sin exponer secretos.
- `GET /api/ai-attack-examples`: ejemplos educativos de ataques IA y defensas esperadas.
- `POST /api/chat`: procesa `{ "message": "texto del usuario", "provider": "local_mock" }` y devuelve respuesta, traza, uso estimado de tokens, seguridad, proveedor, compute, intencion, agente y herramienta. `provider` es opcional y usa `local_mock` por defecto.

## Arquitectura

El frontend envia el mensaje al backend y renderiza la respuesta como tres superficies:

- Panel izquierdo: conversacion.
- Panel central: pipeline animado con React Flow.
- Panel derecho: inspector JSON de la etapa seleccionada y reglas activadas.

El backend esta separado por responsabilidad:

- `schemas.py`: validacion Pydantic y contrato HTTP.
- `services/text_processing.py`: normalizacion, tokenizacion y entidades.
- `services/intent_detector.py`: detector de intenciones por reglas simples.
- `services/openia_intent_reinforcer.py`: refuerzo OpenIA/OpenAI-compatible en modo offline, sin llamadas externas.
- `services/policy_guard.py`: reglas de bloqueo local.
- `services/provider_selection.py`: selecciona `local_mock` u `openai_api` preparado y aplica fallback seguro.
- `services/prompt_builder.py`: muestra como se construye el prompt final para una aplicacion LLM.
- `services/observability.py`: estima tokens, latencia, costo, CPU, RAM y contexto.
- `services/orchestrator.py`: mapeo de intencion a agente y herramienta.
- `agents/`: respuestas deterministas por agente.
- `tools/registry.py`: allowlist de herramientas locales.

## Flujo interno

Cada llamada a `/api/chat` genera estas etapas:

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

Cada etapa devuelve `stage`, `status`, `input_type`, `output_type`, `input`, `output` y `metadata`. El frontend anima la ejecucion y permite inspeccionar cada etapa.

## Reglas de seguridad

El archivo `backend/security_rules.yaml` incluye reglas para:

- No hardcodear tokens.
- Usar variables de entorno para secretos.
- Validar estrictamente entradas.
- Limitar payloads.
- Detectar prompt injection basico.
- Tratar contenido externo como datos.
- Usar allowlist de herramientas.
- Aplicar minimo privilegio.
- Confirmar acciones destructivas.
- Presupuesto maximo de tokens.
- Minimizar contexto.
- No registrar secretos.
- Recomendar HTTPS/TLS.
- Control de acceso por roles.
- Logs estructurados.
- Fallar cerrado ante errores.

El demo bloquea mensajes que parezcan prompt injection, contengan secretos o excedan el presupuesto local de tokens.

## Limitaciones

- No usa modelos reales ni APIs externas.
- El conteo de tokens es una estimacion local simple.
- El costo es ilustrativo y no representa precios vigentes.
- El detector de intenciones usa palabras clave, no aprendizaje automatico.
- El modulo OpenIA/OpenAI-compatible refuerza intenciones en modo offline; no llama APIs externas.
- No ejecuta codigo arbitrario ni implementa acciones destructivas.
- Los logs de auditoria se devuelven en memoria dentro de la respuesta; no hay persistencia.

## Posibles extensiones

- Sustituir el estimador por un tokenizer real.
- Agregar pruebas automatizadas de politicas y pipeline.
- Conectar un proveedor de IA mediante variables de entorno.
- Persistir auditorias redacted en una base de datos.
- Agregar roles y autorizacion para herramientas sensibles.

## Documento de funcionamiento

La explicacion detallada de arquitectura, diagramacion, flujos, contratos, refuerzo OpenIA y ejemplos de ataques IA esta en `docs/FUNCIONAMIENTO_Y_FLUJOS.md`.

## Reporte tecnico

El reporte formal de entrega esta en `docs/REPORTE_TECNICO.md`.

Tambien hay una version LaTeX lista para compilar en `docs/REPORTE_TECNICO.tex`.

El PDF generado esta en `output/pdf/REPORTE_TECNICO.pdf`.

La version HTML imprimible esta en `docs/REPORTE_TECNICO.html`.

## Migracion incremental

El diagnostico, plan y registro de cambios de la reestructuracion esta en `docs/migration_report.md`.

La documentacion de diseno esta en `docs/software_design.md` y los diagramas UML/Mermaid en `docs/uml.md`.

export OPENAI_API_KEY="tu_api_key_aqui"

cd /Users/alberto/Documents/EjemploApp/backend

.venv/bin/python -c "import os; print('OPENAI_API_KEY cargada:', bool(os.getenv('OPENAI_API_KEY'))); print('OPENAI_MODEL:', os.getenv('OPENAI_MODEL'))"
