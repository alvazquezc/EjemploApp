from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    LongTable,
    PageBreak,
    PageTemplate,
    Paragraph,
    Preformatted,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "pdf" / "REPORTE_TECNICO.pdf"


class NumberedCanvas:
    def __init__(self) -> None:
        self.pages = []

    def __call__(self, canvas, doc) -> None:
        canvas.saveState()
        width, height = letter
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#475569"))
        canvas.drawString(2.0 * cm, height - 1.25 * cm, "Demo chatbot con agente orquestador")
        canvas.drawRightString(width - 2.0 * cm, height - 1.25 * cm, f"Pagina {doc.page}")
        canvas.setStrokeColor(colors.HexColor("#CBD5E1"))
        canvas.line(2.0 * cm, height - 1.45 * cm, width - 2.0 * cm, height - 1.45 * cm)
        canvas.restoreState()


def styles():
    base = getSampleStyleSheet()
    base.add(
        ParagraphStyle(
            name="CoverTitle",
            parent=base["Title"],
            fontName="Helvetica-Bold",
            fontSize=28,
            leading=34,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#14283C"),
            spaceAfter=14,
        )
    )
    base.add(
        ParagraphStyle(
            name="CoverSubtitle",
            parent=base["Normal"],
            fontSize=14,
            leading=20,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#334155"),
            spaceAfter=12,
        )
    )
    base.add(
        ParagraphStyle(
            name="Section",
            parent=base["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=16,
            leading=21,
            textColor=colors.HexColor("#14283C"),
            spaceBefore=14,
            spaceAfter=8,
        )
    )
    base.add(
        ParagraphStyle(
            name="Subsection",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=16,
            textColor=colors.HexColor("#1F3B57"),
            spaceBefore=10,
            spaceAfter=6,
        )
    )
    base.add(
        ParagraphStyle(
            name="Body",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=13.2,
            alignment=TA_LEFT,
            spaceAfter=7,
        )
    )
    base.add(
        ParagraphStyle(
            name="BulletBody",
            parent=base["Body"],
            leftIndent=14,
            firstLineIndent=-8,
            bulletIndent=0,
        )
    )
    base.add(
        ParagraphStyle(
            name="TableHeader",
            parent=base["Body"],
            fontName="Helvetica-Bold",
            textColor=colors.white,
            alignment=TA_CENTER,
        )
    )
    base.add(
        ParagraphStyle(
            name="TableCell",
            parent=base["Body"],
            fontSize=8.2,
            leading=11,
            spaceAfter=0,
        )
    )
    return base


def p(text: str, style_name: str = "Body") -> Paragraph:
    return Paragraph(text, STYLES[style_name])


def section(number: str, title: str):
    return p(f"{number}. {title}", "Section")


def subsection(number: str, title: str):
    return p(f"{number}. {title}", "Subsection")


def bullets(items: list[str]):
    return [p(f"- {item}", "BulletBody") for item in items]


def code_block(text: str):
    return Preformatted(
        text,
        ParagraphStyle(
            name="Code",
            fontName="Courier",
            fontSize=7.6,
            leading=10,
            backColor=colors.HexColor("#F5F7FA"),
            borderColor=colors.HexColor("#D2DAE2"),
            borderWidth=0.5,
            borderPadding=6,
            leftIndent=0,
            rightIndent=0,
            spaceBefore=4,
            spaceAfter=10,
        ),
    )


def table(data: list[list[str]], widths: list[float] | None = None, long: bool = False):
    formatted = []
    for row_index, row in enumerate(data):
        style = "TableHeader" if row_index == 0 else "TableCell"
        formatted.append([p(cell, style) for cell in row])
    cls = LongTable if long else Table
    t = cls(formatted, colWidths=widths, repeatRows=1 if long else 0)
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F3B57")),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#CBD5E1")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#FFFFFF")),
            ]
        )
    )
    return t


def cover():
    return [
        Spacer(1, 2.2 * cm),
        p("Reporte tecnico", "CoverTitle"),
        p("Demo web de chatbot con agente orquestador", "CoverSubtitle"),
        p(
            "Detector de intenciones, refuerzo OpenIA offline y visualizacion de flujo de tokens",
            "CoverSubtitle",
        ),
        Spacer(1, 2.0 * cm),
        table(
            [
                ["Campo", "Valor"],
                ["Proyecto", "EjemploApp"],
                ["Stack", "React + Vite + TypeScript / FastAPI + Pydantic"],
                ["Modalidad", "Demo local sin APIs externas"],
                ["Documento", "Reporte de entrega"],
            ],
            widths=[4.2 * cm, 10.0 * cm],
        ),
        PageBreak(),
    ]


def build_story():
    story = []
    story.extend(cover())
    story.append(p("Indice", "Section"))
    toc_items = [
        "1. Resumen ejecutivo",
        "2. Alcance implementado",
        "3. Estructura del proyecto",
        "4. Arquitectura general",
        "5. Backend",
        "6. Modulo OpenIA/OpenAI-compatible",
        "7. Frontend",
        "8. Seguridad implementada",
        "9. Ejemplos de ataques IA incluidos",
        "10. Evidencia de validacion",
        "11. Limitaciones del demo",
        "12. Posibles extensiones",
        "13. Conclusiones",
    ]
    for item in toc_items:
        story.append(p(item, "Body"))
    story.append(PageBreak())

    story.append(section("1", "Resumen ejecutivo"))
    story.append(
        p(
            "Se desarrollo un demo web funcional de una aplicacion tipo chatbot con agente orquestador, "
            "detector de intenciones, refuerzo OpenIA/OpenAI-compatible en modo offline, reglas de "
            "ciberseguridad y visualizacion interna del flujo de tokens."
        )
    )
    story.append(
        p(
            "La aplicacion permite que un usuario escriba un mensaje, lo procese en backend por etapas y "
            "visualice en frontend el flujo completo mediante nodos secuenciales, inspector tecnico JSON, "
            "metricas de tokens, intencion detectada, agente seleccionado, herramienta ejecutada y reglas "
            "de seguridad aplicadas."
        )
    )
    story.append(p("El demo corre localmente sin APIs externas, sin claves reales y sin ejecutar codigo arbitrario."))

    story.append(section("2", "Alcance implementado"))
    story.extend(
        bullets(
            [
                "Frontend en React + Vite + TypeScript.",
                "Visualizacion de flujo con React Flow.",
                "Backend en Python + FastAPI.",
                "Validacion de requests y respuestas con Pydantic.",
                "Reglas de ciberseguridad en YAML.",
                "Pipeline trazable por etapas.",
                "Detector de intenciones por reglas.",
                "Modulo de refuerzo de intencion OpenIA/OpenAI-compatible en modo offline.",
                "Orquestador de agentes.",
                "Allowlist de herramientas locales.",
                "Ejemplos educativos de ataques de IA.",
                "Documentacion tecnica con diagramas y flujos.",
            ]
        )
    )

    story.append(section("3", "Estructura del proyecto"))
    story.append(
        code_block(
            """EjemploApp/
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
    REPORTE_TECNICO.tex
  README.md"""
        )
    )

    story.append(section("4", "Arquitectura general"))
    story.append(
        table(
            [
                ["Componente", "Responsabilidad"],
                ["Frontend React", "Captura mensajes, renderiza chat, muestra metricas, visualiza nodos y permite inspeccionar etapas."],
                ["FastAPI", "Expone endpoints HTTP y valida contratos con Pydantic."],
                ["Pipeline", "Ejecuta las etapas secuenciales y genera trazas estructuradas."],
                ["Detector de intencion", "Clasifica la solicitud inicial mediante reglas simples."],
                ["Refuerzo OpenIA", "Ajusta la intencion en modo offline con senales semanticas locales."],
                ["Policy guard", "Bloquea prompt injection, secretos y exceso de presupuesto."],
                ["Orquestador", "Selecciona agente y herramienta segun la intencion final."],
                ["Agentes", "Generan respuestas deterministas locales."],
                ["Herramientas", "Ejecutan funciones permitidas por allowlist."],
            ],
            widths=[4.2 * cm, 10.4 * cm],
            long=True,
        )
    )

    story.append(section("5", "Backend"))
    story.append(p("El backend expone una API FastAPI con tres responsabilidades principales:"))
    story.extend(bullets(["Recibir mensajes del usuario.", "Ejecutar el pipeline interno.", "Devolver una respuesta estructurada con trazas, seguridad, tokens e intencion."]))
    story.append(subsection("5.1", "Endpoints"))
    story.append(
        table(
            [
                ["Metodo", "Endpoint", "Funcion"],
                ["GET", "/api/health", "Verifica estado del servicio."],
                ["GET", "/api/security-rules", "Devuelve reglas cargadas desde YAML."],
                ["GET", "/api/ai-attack-examples", "Devuelve ejemplos educativos de ataques IA."],
                ["POST", "/api/chat", "Procesa el mensaje y devuelve respuesta, traza, seguridad, tokens, intencion, agente y herramienta."],
            ],
            widths=[2.2 * cm, 4.4 * cm, 8.0 * cm],
        )
    )
    story.append(subsection("5.2", "Pipeline implementado"))
    story.extend(
        bullets(
            [
                "raw_input",
                "normalization",
                "tokenization",
                "entity_extraction",
                "intent_detection",
                "intent_reinforcement",
                "policy_guard",
                "orchestrator",
                "agent_selection",
                "tool_execution",
                "response_generation",
                "audit_log",
            ]
        )
    )
    story.append(p("Cada etapa genera los campos stage, status, input_type, output_type, input, output y metadata."))

    story.append(section("6", "Modulo OpenIA/OpenAI-compatible"))
    story.append(
        p(
            "Se agrego el modulo openia_intent_reinforcer.py. Su funcion es reforzar la intencion detectada "
            "usando una capa semantica local. No llama a APIs externas y no requiere OPENAI_API_KEY."
        )
    )
    story.extend(
        bullets(
            [
                "Si la intencion base es unknown_intent o general_question, puede reemplazarla por una intencion mas especifica cuando encuentra senales suficientes.",
                "Si la intencion base ya es especifica, puede conservarla y elevar la confianza.",
                "Si no encuentra senales utiles, conserva la intencion original.",
                "Si se configura un modo externo no soportado, no realiza llamadas de red y reporta que el modo externo no esta habilitado.",
            ]
        )
    )
    story.append(code_block("Entrada: tokens\nIntencion base: unknown_intent\nIntencion final: explain_tokens\nRefuerzo aplicado: true\nEtapas de traza: 12"))

    story.append(section("7", "Frontend"))
    story.append(p("El frontend esta organizado en tres paneles:"))
    story.extend(bullets(["Panel izquierdo: chat.", "Panel central: flujo React Flow y metricas.", "Panel derecho: inspector tecnico."]))
    story.append(
        p(
            "La interfaz muestra conversacion, nodos del pipeline, estado de cada etapa, JSON de entrada y salida, "
            "conteo estimado de tokens, costo ilustrativo, politica de seguridad, refuerzo OpenIA, agente "
            "seleccionado, herramienta ejecutada, reglas activadas y ejemplos defensivos de ataques IA."
        )
    )

    story.append(section("8", "Seguridad implementada"))
    story.extend(
        bullets(
            [
                "Validacion Pydantic para requests.",
                "Rechazo de mensajes vacios.",
                "Limite de longitud del mensaje.",
                "Deteccion simple de prompt injection.",
                "Deteccion de texto con forma de secreto.",
                "Redaccion de secretos en trazas.",
                "Allowlist de herramientas.",
                "Bloqueo fail closed ante politica insegura.",
                "Sin ejecucion arbitraria de codigo.",
                "Sin endpoints destructivos.",
                "Sin uso de claves reales.",
                "Sin servicios pagos ni APIs externas.",
            ]
        )
    )

    story.append(section("9", "Ejemplos de ataques IA incluidos"))
    story.append(
        table(
            [
                ["Categoria", "Ejemplo resumido", "Defensa esperada"],
                ["Prompt injection directa", "Ignorar instrucciones anteriores.", "Detectar bypass y bloquear."],
                ["Extraccion de prompt interno", "Pedir prompts o politicas internas.", "No revelar configuracion interna."],
                ["Abuso de herramientas", "Forzar herramientas no autorizadas.", "Aplicar allowlist."],
                ["Inyeccion indirecta", "Documento externo intenta dar instrucciones.", "Tratar contenido externo como datos."],
                ["Secreto en entrada", "Usuario pega token o API key.", "Redactar y bloquear segun politica."],
                ["Accion destructiva", "Saltar confirmacion para eliminar datos.", "Requerir confirmacion y permisos."],
            ],
            widths=[4.2 * cm, 5.0 * cm, 5.4 * cm],
            long=True,
        )
    )

    story.append(section("10", "Evidencia de validacion"))
    story.append(subsection("10.1", "Backend"))
    story.append(code_block("python -m compileall -q app\npip check"))
    story.append(code_block("No broken requirements found."))
    story.append(code_block('/api/health -> OK\n/api/ai-attack-examples -> 6 ejemplos\n/api/chat con "tokens" -> explain_tokens, refuerzo aplicado, 12 etapas\n/api/chat con prompt injection -> bloqueado, 12 etapas'))
    story.append(subsection("10.2", "Frontend"))
    story.append(code_block("npm run build\nnpm audit --audit-level=moderate"))
    story.append(code_block("TypeScript compila sin errores.\nVite genera bundle de produccion.\n0 vulnerabilities."))

    story.append(section("11", "Limitaciones del demo"))
    story.extend(bullets(["No usa modelos reales.", "No llama a OpenAI ni a otro proveedor externo.", "El conteo de tokens es aproximado.", "El costo es ilustrativo.", "El detector de intenciones es determinista.", "No persiste auditorias en base de datos.", "No implementa autenticacion ni roles reales."]))

    story.append(section("12", "Posibles extensiones"))
    story.extend(bullets(["Integrar OpenAI real mediante una bandera explicita y OPENAI_API_KEY en variable de entorno.", "Validar salidas de modelo con esquemas estrictos.", "Agregar pruebas automatizadas con pytest.", "Persistir auditoria redacted.", "Agregar autenticacion y RBAC.", "Sustituir el estimador por un tokenizer real.", "Exportar trazas como JSON o PDF.", "Agregar vista de comparacion entre intencion base e intencion reforzada."]))

    story.append(section("13", "Conclusiones"))
    story.append(p("El demo cumple el objetivo de mostrar de forma educativa lo que ocurre internamente cuando un chatbot procesa un mensaje. La arquitectura separa frontend, backend, reglas, agentes, herramientas, seguridad y trazabilidad."))
    story.append(p("La aplicacion queda lista para demostraciones locales y como base para futuras integraciones reales, manteniendo por defecto un modo seguro, offline y sin secretos."))

    return story


def build_pdf():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc = BaseDocTemplate(
        str(OUTPUT),
        pagesize=letter,
        leftMargin=2.0 * cm,
        rightMargin=2.0 * cm,
        topMargin=2.0 * cm,
        bottomMargin=2.0 * cm,
        title="Reporte tecnico del demo web",
        author="Codex",
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="normal")
    template = PageTemplate(id="report", frames=[frame], onPage=NumberedCanvas())
    doc.addPageTemplates([template])
    doc.build(build_story())
    return OUTPUT


STYLES = styles()


if __name__ == "__main__":
    path = build_pdf()
    print(path)
