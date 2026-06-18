import { Bot, BrainCircuit, Coins, Server, ShieldCheck, Split, Wrench } from "lucide-react";
import type { ChatResponse } from "../types/api";

interface MetricBarProps {
  response: ChatResponse | null;
}

function formatCost(value: number | undefined) {
  if (!value) {
    return "$0.000000";
  }
  return `$${value.toFixed(6)}`;
}

export function MetricBar({ response }: MetricBarProps) {
  const tokenUsage = response?.token_usage;
  const securityStatus = response?.security.allowed === false ? "Bloqueado" : "Permitido";

  return (
    <div className="metric-bar">
      <div className="metric">
        <Split size={16} />
        <span>Tokens</span>
        <strong>{tokenUsage?.total_tokens ?? 0}</strong>
      </div>
      <div className="metric">
        <Coins size={16} />
        <span>Costo</span>
        <strong>{formatCost(response?.estimated_cost_usd)}</strong>
      </div>
      <div className="metric">
        <ShieldCheck size={16} />
        <span>Politica</span>
        <strong>{securityStatus}</strong>
      </div>
      <div className="metric">
        <BrainCircuit size={16} />
        <span>OpenIA</span>
        <strong>{response?.intent_reinforcement.changed ? "Ajustada" : response ? "Revisada" : "Pendiente"}</strong>
      </div>
      <div className="metric">
        <Server size={16} />
        <span>Proveedor</span>
        <strong>{response?.provider.selected_provider ?? "Pendiente"}</strong>
      </div>
      <div className="metric">
        <Bot size={16} />
        <span>Agente</span>
        <strong>{response?.agent ?? "Pendiente"}</strong>
      </div>
      <div className="metric">
        <Wrench size={16} />
        <span>Herramienta</span>
        <strong>{response?.tool ?? "Ninguna"}</strong>
      </div>
    </div>
  );
}
