import { Activity, Cpu, Gauge, HardDrive, Server, Sigma } from "lucide-react";
import type { ChatResponse } from "../types/api";

interface ComputeDashboardProps {
  response: ChatResponse | null;
}

function formatCost(value: number | undefined) {
  return `$${(value ?? 0).toFixed(6)}`;
}

export function ComputeDashboard({ response }: ComputeDashboardProps) {
  const compute = response?.compute;

  return (
    <section className="compute-dashboard" aria-label="Dashboard Token y Compute">
      <div className="dashboard-title">
        <Activity size={16} />
        <span>Token & Compute</span>
      </div>
      <div className="compute-grid">
        <div>
          <Server size={15} />
          <span>Proveedor</span>
          <strong>{compute?.provider ?? "local_mock"}</strong>
        </div>
        <div>
          <Gauge size={15} />
          <span>Modelo</span>
          <strong>{compute?.model ?? "Pendiente"}</strong>
        </div>
        <div>
          <Sigma size={15} />
          <span>Tokens</span>
          <strong>{compute?.total_tokens ?? 0}</strong>
        </div>
        <div>
          <Activity size={15} />
          <span>Latencia</span>
          <strong>{compute?.latency_ms ?? 0} ms</strong>
        </div>
        <div>
          <Cpu size={15} />
          <span>CPU local</span>
          <strong>{compute?.estimated_cpu_ms ?? 0} ms</strong>
        </div>
        <div>
          <HardDrive size={15} />
          <span>RAM local</span>
          <strong>{compute?.estimated_ram_mb ?? 0} MB</strong>
        </div>
        <div>
          <Sigma size={15} />
          <span>Contexto</span>
          <strong>{compute?.estimated_context_tokens ?? 0}</strong>
        </div>
        <div>
          <Gauge size={15} />
          <span>Costo</span>
          <strong>{formatCost(compute?.estimated_cost_usd)}</strong>
        </div>
      </div>
      <p>{compute?.mode_note ?? "Ejecuta un mensaje para comparar consumo local y arquitectura OpenAI API."}</p>
    </section>
  );
}
