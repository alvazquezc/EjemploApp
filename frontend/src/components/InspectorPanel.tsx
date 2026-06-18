import { Activity, BrainCircuit, FileJson, ShieldAlert } from "lucide-react";
import type { AIAttackExample, ChatResponse, SecurityRule, TraceStep } from "../types/api";

interface InspectorPanelProps {
  selectedStep: TraceStep | null;
  response: ChatResponse | null;
  rules: SecurityRule[];
  attackExamples: AIAttackExample[];
}

export function InspectorPanel({ selectedStep, response, rules, attackExamples }: InspectorPanelProps) {
  const triggered = new Set(response?.security.triggered_rules ?? []);
  const visibleTriggeredRules = rules.filter((rule) => triggered.has(rule.id));
  const visibleAttackExamples = attackExamples.slice(0, 4);

  return (
    <section className="panel inspector-panel" aria-label="Inspector">
      <header className="panel-header">
        <div>
          <p className="eyebrow">Inspector</p>
          <h2>{selectedStep?.stage ?? "Sin etapa"}</h2>
        </div>
      </header>

      <div className="inspector-section">
        <div className="section-title">
          <Activity size={15} />
          Resultado
        </div>
        <dl className="kv-grid">
          <div>
            <dt>Intencion</dt>
            <dd>{response?.intent ?? "Pendiente"}</dd>
          </div>
          <div>
            <dt>Refuerzo</dt>
            <dd>{response?.intent_reinforcement.provider ?? "Pendiente"}</dd>
          </div>
          <div>
            <dt>Agente</dt>
            <dd>{response?.agent ?? "Pendiente"}</dd>
          </div>
          <div>
            <dt>Proveedor</dt>
            <dd>{response?.provider.selected_provider ?? "Pendiente"}</dd>
          </div>
          <div>
            <dt>Estado</dt>
            <dd>{selectedStep?.status ?? "pending"}</dd>
          </div>
          <div>
            <dt>Tipo</dt>
            <dd>{selectedStep?.output_type ?? "Pendiente"}</dd>
          </div>
        </dl>
      </div>

      <div className="inspector-section">
        <div className="section-title">
          <BrainCircuit size={15} />
          Refuerzo OpenIA
        </div>
        <dl className="kv-grid">
          <div>
            <dt>Original</dt>
            <dd>{response?.intent_reinforcement.original_intent ?? "Pendiente"}</dd>
          </div>
          <div>
            <dt>Final</dt>
            <dd>{response?.intent_reinforcement.final_intent ?? "Pendiente"}</dd>
          </div>
          <div>
            <dt>Confianza</dt>
            <dd>{response ? response.intent_reinforcement.confidence.toFixed(2) : "0.00"}</dd>
          </div>
          <div>
            <dt>Cambio</dt>
            <dd>{response?.intent_reinforcement.changed ? "Si" : "No"}</dd>
          </div>
        </dl>
      </div>

      <div className="inspector-section">
        <div className="section-title">
          <ShieldAlert size={15} />
          Reglas activadas
        </div>
        {visibleTriggeredRules.length > 0 ? (
          <ul className="rule-list">
            {visibleTriggeredRules.map((rule) => (
              <li key={rule.id} className={`severity-${rule.severity}`}>
                <strong>{rule.title}</strong>
                <span>{rule.description}</span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="empty-state">Sin reglas activadas</p>
        )}
      </div>

      <div className="inspector-section">
        <div className="section-title">
          <ShieldAlert size={15} />
          Ataques IA
        </div>
        <ul className="attack-list">
          {visibleAttackExamples.map((example) => (
            <li key={example.id}>
              <strong>{example.title}</strong>
              <code>{example.sample_instruction}</code>
              <span>{example.expected_defense}</span>
            </li>
          ))}
        </ul>
      </div>

      <div className="inspector-section json-section">
        <div className="section-title">
          <FileJson size={15} />
          JSON
        </div>
        <pre>{JSON.stringify(selectedStep ?? {}, null, 2)}</pre>
      </div>
    </section>
  );
}
