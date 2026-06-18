# Reporte tecnico del demo web

## 1. Resumen ejecutivo

Se desarrollo un demo web funcional de una aplicacion tipo chatbot con agente orquestador, detector de intenciones, refuerzo OpenIA/OpenAI-compatible en modo offline, reglas de ciberseguridad y visualizacion interna del flujo de tokens.

La aplicacion permite que un usuario escriba un mensaje, lo procese en backend por etapas y visualice en frontend el flujo completo mediante nodos secuenciales, inspector tecnico JSON, metricas de tokens, intencion detectada, agente seleccionado, herramienta ejecutada y reglas de seguridad aplicadas.

El demo corre localmente sin APIs externas, sin claves reales y sin ejecutar codigo arbitrario.

## 2. Alcance implementado

- Frontend en React + Vite + TypeScript.
- Visualizacion de flujo con React Flow.
- Backend en Python + FastAPI.
- Validacion de requests y respuestas con Pydantic.
- Reglas de ciberseguridad en YAML.
- Pipeline trazable por etapas.
- Detector de intenciones por reglas.
- Modulo de refuerzo de intencion `OpenIA/OpenAI-compatible` en modo offline.
- Orquestador de agentes.
- Allowlist de herramientas locales.
- Ejemplos educativos de ataques de IA.
- Documentacion tecnica con diagramas y flujos.

## 3. Estructura del proyecto

```text
EjemploApp/
  backend/
    app/
      agents/
      services/
      tools/
      main.py
      schemas.py
    security_rules.yaml
    requirements.txt
  frontend/
    src/
      components/
      services/
      styles/
      types/
      App.tsx
    package.json
    vite.config.ts
  docs/
    FUNCIONAMIENTO_Y_FLUJOS.md
    REPORTE_TECNICO.md
  README.md
```

## 4. Backend

El backend expone una API FastAPI con tres responsabilidades principales:

1. Recibir mensajes del usuario.
2. Ejecutar el pipeline interno.
3. Devolver una respuesta estructurada con trazas, seguridad, tokens e intencion.

### Endpoints

| Metodo | Endpoint | Funcion |
| --- | --- | --- |
| `GET` | `/api/health` | Verifica estado del servicio |
| `GET` | `/api/security-rules` | Devuelve reglas cargadas desde YAML |
| `GET` | `/api/ai-attack-examples` | Devuelve ejemplos educativos de ataques IA |
| `POST` | `/api/chat` | Procesa el mensaje y devuelve respuesta + traza |

### Pipeline implementado

1. `raw_input`
2. `normalization`
3. `tokenization`
4. `entity_extraction`
5. `intent_detection`
6. `intent_reinforcement`
7. `policy_guard`
8. `orchestrator`
9. `agent_selection`
10. `tool_execution`
11. `response_generation`
12. `audit_log`

Cada etapa genera:

- `stage`
- `status`
- `input_type`
- `output_type`
- `input`
- `output`
- `metadata`

## 5. Modulo OpenIA/OpenAI-compatible

Se agrego un modulo llamado `openia_intent_reinforcer.py`.

Su funcion es reforzar la intencion detectada usando una capa semantica local. No llama a APIs externas y no requiere `OPENAI_API_KEY`.

Comportamiento:

- Si la intencion base es `unknown_intent` o `general_question`, puede reemplazarla por una intencion mas especifica cuando encuentra senales suficientes.
- Si la intencion base ya es especifica, puede conservarla y elevar la confianza.
- Si no encuentra senales utiles, conserva la intencion original.

Ejemplo validado:

```text
Entrada: tokens
Intencion base: unknown_intent
Intencion final: explain_tokens
Refuerzo aplicado: true
Etapas de traza: 12
```

## 6. Frontend

El frontend esta organizado en tres paneles:

- Panel izquierdo: chat.
- Panel central: flujo React Flow y metricas.
- Panel derecho: inspector tecnico.

La interfaz muestra:

- Conversacion.
- Nodos del pipeline.
- Estado de cada etapa.
- JSON de entrada, salida y metadatos.
- Conteo estimado de tokens.
- Costo estimado ilustrativo.
- Politica permitida o bloqueada.
- Refuerzo OpenIA.
- Agente seleccionado.
- Herramienta ejecutada.
- Reglas de seguridad activadas.
- Ejemplos defensivos de ataques IA.

## 7. Seguridad implementada

El sistema incorpora controles de seguridad basicos:

- Validacion Pydantic para requests.
- Rechazo de mensajes vacios.
- Limite de longitud del mensaje.
- Deteccion simple de prompt injection.
- Deteccion de texto con forma de secreto.
- Redaccion de secretos en trazas.
- Allowlist de herramientas.
- Bloqueo fail closed ante politica insegura.
- Sin ejecucion arbitraria de codigo.
- Sin endpoints destructivos.
- Sin uso de claves reales.
- Sin servicios pagos ni APIs externas.

## 8. Ejemplos de ataques IA incluidos

El endpoint `/api/ai-attack-examples` devuelve ejemplos educativos para explicar riesgos y defensas:

- Inyeccion directa contra instrucciones.
- Extraccion de prompt interno.
- Abuso de herramientas.
- Inyeccion indirecta en contenido externo.
- Secreto incluido por el usuario.
- Presion para accion destructiva.

Estos ejemplos son defensivos y estan orientados a explicar deteccion y mitigacion.

## 9. Evidencia de validacion

Se ejecutaron validaciones de backend y frontend.

### Backend

```bash
python -m compileall -q app
pip check
```

Resultado:

```text
No broken requirements found.
```

Pruebas funcionales:

```text
/api/health -> OK
/api/ai-attack-examples -> 6 ejemplos
/api/chat con "tokens" -> explain_tokens, refuerzo aplicado, 12 etapas
/api/chat con prompt injection -> bloqueado, 12 etapas
```

### Frontend

```bash
npm run build
npm audit --audit-level=moderate
```

Resultado:

```text
TypeScript compila sin errores.
Vite genera bundle de produccion.
0 vulnerabilities.
```

## 10. Limitaciones del demo

- No usa modelos reales.
- No llama a OpenAI ni a otro proveedor externo.
- El conteo de tokens es aproximado.
- El costo es ilustrativo.
- El detector de intenciones es determinista.
- No persiste auditorias en base de datos.
- No implementa autenticacion ni roles reales.

## 11. Posibles extensiones

- Integrar OpenAI real mediante una bandera explicita y `OPENAI_API_KEY` en variable de entorno.
- Validar salidas de modelo con esquemas estrictos.
- Agregar pruebas automatizadas con `pytest`.
- Persistir auditoria redacted.
- Agregar autenticacion y RBAC.
- Sustituir el estimador por un tokenizer real.
- Exportar trazas como JSON o PDF.
- Agregar vista de comparacion entre intencion base e intencion reforzada.

## 12. Conclusiones

El demo cumple el objetivo de mostrar de forma educativa lo que ocurre internamente cuando un chatbot procesa un mensaje. La arquitectura separa frontend, backend, reglas, agentes, herramientas, seguridad y trazabilidad.

La aplicacion queda lista para demostraciones locales y como base para futuras integraciones reales, manteniendo por defecto un modo seguro, offline y sin secretos.

