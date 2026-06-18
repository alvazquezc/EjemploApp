import type { TraceStep, TraceStatus } from "../types/api";

type GifPalette = number[][];
type GifModule = {
  GIFEncoder: () => {
    writeFrame(
      index: Uint8Array,
      width: number,
      height: number,
      options?: { palette?: GifPalette; delay?: number },
    ): void;
    finish(): void;
    bytes(): Uint8Array;
  };
  quantize: (rgba: Uint8Array | Uint8ClampedArray, maxColors: number) => GifPalette;
  applyPalette: (rgba: Uint8Array | Uint8ClampedArray, palette: GifPalette) => Uint8Array;
};

const STAGE_LABELS: Record<string, string> = {
  raw_input: "raw_input",
  normalization: "normalization",
  tokenization: "tokenization",
  entity_extraction: "entity_extraction",
  intent_detection: "intent_detection",
  intent_reinforcement: "intent_reinforcement",
  policy_guard: "policy_guard",
  provider_selection: "provider_selection",
  orchestrator: "orchestrator",
  prompt_builder: "prompt_builder",
  agent_selection: "agent_selection",
  tool_execution: "tool_execution",
  provider_execution: "provider_execution",
  response_generation: "response_generation",
  audit_log: "audit_log",
};

const STATUS_COLORS: Record<TraceStatus, { fill: string; stroke: string; text: string }> = {
  pending: { fill: "#ffffff", stroke: "#cbd5e1", text: "#64748b" },
  active: { fill: "#e9fbf7", stroke: "#0f9f8f", text: "#0f766e" },
  completed: { fill: "#f2fbf8", stroke: "#63bdae", text: "#134e4a" },
  blocked: { fill: "#fffbeb", stroke: "#f59e0b", text: "#92400e" },
  error: { fill: "#fef2f2", stroke: "#ef4444", text: "#991b1b" },
};

const WIDTH = 1120;
const HEIGHT = 720;
const NODE_WIDTH = 238;
const NODE_HEIGHT = 82;
const GAP_X = 110;
const GAP_Y = 42;
const START_X = 62;
const START_Y = 120;

function roundedRect(ctx: CanvasRenderingContext2D, x: number, y: number, width: number, height: number, radius: number) {
  const right = x + width;
  const bottom = y + height;
  ctx.beginPath();
  ctx.moveTo(x + radius, y);
  ctx.lineTo(right - radius, y);
  ctx.quadraticCurveTo(right, y, right, y + radius);
  ctx.lineTo(right, bottom - radius);
  ctx.quadraticCurveTo(right, bottom, right - radius, bottom);
  ctx.lineTo(x + radius, bottom);
  ctx.quadraticCurveTo(x, bottom, x, bottom - radius);
  ctx.lineTo(x, y + radius);
  ctx.quadraticCurveTo(x, y, x + radius, y);
  ctx.closePath();
}

function drawText(ctx: CanvasRenderingContext2D, text: string, x: number, y: number, maxWidth: number) {
  const value = ctx.measureText(text).width > maxWidth ? `${text.slice(0, 24)}...` : text;
  ctx.fillText(value, x, y);
}

function stagePosition(index: number) {
  const column = index % 3;
  const row = Math.floor(index / 3);
  return {
    x: START_X + column * (NODE_WIDTH + GAP_X),
    y: START_Y + row * (NODE_HEIGHT + GAP_Y),
  };
}

function drawArrow(ctx: CanvasRenderingContext2D, fromX: number, fromY: number, toX: number, toY: number, active: boolean) {
  ctx.save();
  ctx.strokeStyle = active ? "#0f9f8f" : "#cbd5e1";
  ctx.fillStyle = active ? "#0f9f8f" : "#cbd5e1";
  ctx.lineWidth = active ? 3 : 2;
  ctx.setLineDash(active ? [7, 7] : [4, 7]);
  ctx.beginPath();
  ctx.moveTo(fromX, fromY);
  ctx.lineTo(toX, toY);
  ctx.stroke();
  ctx.setLineDash([]);
  const angle = Math.atan2(toY - fromY, toX - fromX);
  ctx.beginPath();
  ctx.moveTo(toX, toY);
  ctx.lineTo(toX - 10 * Math.cos(angle - Math.PI / 6), toY - 10 * Math.sin(angle - Math.PI / 6));
  ctx.lineTo(toX - 10 * Math.cos(angle + Math.PI / 6), toY - 10 * Math.sin(angle + Math.PI / 6));
  ctx.closePath();
  ctx.fill();
  ctx.restore();
}

function drawFrame(ctx: CanvasRenderingContext2D, trace: TraceStep[], currentIndex: number) {
  ctx.fillStyle = "#f6f8fb";
  ctx.fillRect(0, 0, WIDTH, HEIGHT);

  ctx.fillStyle = "#17202a";
  ctx.font = "700 28px Inter, Arial, sans-serif";
  ctx.fillText("Secuencia del agente orquestador", 42, 52);
  ctx.fillStyle = "#637083";
  ctx.font = "500 16px Inter, Arial, sans-serif";
  ctx.fillText(`Paso ${Math.min(currentIndex + 1, trace.length)} de ${trace.length}: ${trace[currentIndex]?.stage ?? "pipeline"}`, 42, 82);

  for (let x = 28; x < WIDTH; x += 18) {
    for (let y = 104; y < HEIGHT; y += 18) {
      ctx.fillStyle = "#dbe4ec";
      ctx.fillRect(x, y, 1, 1);
    }
  }

  trace.slice(0, -1).forEach((_, index) => {
    const from = stagePosition(index);
    const to = stagePosition(index + 1);
    drawArrow(
      ctx,
      from.x + NODE_WIDTH,
      from.y + NODE_HEIGHT / 2,
      to.x,
      to.y + NODE_HEIGHT / 2,
      index < currentIndex,
    );
  });

  trace.forEach((step, index) => {
    const position = stagePosition(index);
    const isActive = index === currentIndex;
    const status = index < currentIndex ? "completed" : isActive ? "active" : step.status === "blocked" ? "blocked" : "pending";
    const colors = STATUS_COLORS[status];

    ctx.save();
    if (isActive) {
      ctx.shadowColor = "rgba(15, 159, 143, 0.28)";
      ctx.shadowBlur = 18;
    }
    roundedRect(ctx, position.x, position.y, NODE_WIDTH, NODE_HEIGHT, 9);
    ctx.fillStyle = colors.fill;
    ctx.fill();
    ctx.shadowBlur = 0;
    ctx.lineWidth = isActive ? 3 : 1.5;
    ctx.strokeStyle = colors.stroke;
    ctx.stroke();
    ctx.restore();

    ctx.fillStyle = "#17202a";
    ctx.font = "800 16px Inter, Arial, sans-serif";
    drawText(ctx, STAGE_LABELS[step.stage] ?? step.stage, position.x + 16, position.y + 30, NODE_WIDTH - 32);
    ctx.fillStyle = colors.text;
    ctx.font = "700 12px Inter, Arial, sans-serif";
    ctx.fillText(status.toUpperCase(), position.x + 16, position.y + 52);
    ctx.fillStyle = "#64748b";
    ctx.font = "500 12px Inter, Arial, sans-serif";
    drawText(ctx, step.output_type || step.input_type, position.x + 16, position.y + 69, NODE_WIDTH - 32);
  });
}

export async function exportTraceGif(trace: TraceStep[]) {
  if (!trace.length) {
    return;
  }

  const loadModule = new Function("url", "return import(url)") as (url: string) => Promise<GifModule>;
  const { GIFEncoder, applyPalette, quantize } = await loadModule("/vendor/gifenc.esm.js");

  const canvas = document.createElement("canvas");
  canvas.width = WIDTH;
  canvas.height = HEIGHT;
  const ctx = canvas.getContext("2d");
  if (!ctx) {
    throw new Error("No se pudo crear el canvas para exportar GIF.");
  }

  const gif = GIFEncoder();
  trace.forEach((_, index) => {
    drawFrame(ctx, trace, index);
    const data = ctx.getImageData(0, 0, WIDTH, HEIGHT).data;
    const palette = quantize(data, 128);
    const indexed = applyPalette(data, palette);
    gif.writeFrame(indexed, WIDTH, HEIGHT, { palette, delay: index === trace.length - 1 ? 1200 : 520 });
  });
  gif.finish();

  const blob = new Blob([gif.bytes()], { type: "image/gif" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `secuencia-agente-${new Date().toISOString().slice(0, 19).replace(/[:T]/g, "-")}.gif`;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}
