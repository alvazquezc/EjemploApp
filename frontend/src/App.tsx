import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { ChatPanel } from "./components/ChatPanel";
import { ComputeDashboard } from "./components/ComputeDashboard";
import { FlowPanel } from "./components/FlowPanel";
import { InspectorPanel } from "./components/InspectorPanel";
import { MetricBar } from "./components/MetricBar";
import { fetchAIAttackExamples, fetchProviderStatus, fetchSecurityRules, sendChatMessage } from "./services/api";
import type { AIAttackExample, ChatMessage, ChatResponse, ProviderName, ProviderStatus, SecurityRule, TraceStep } from "./types/api";

const STAGES = [
  "raw_input",
  "normalization",
  "tokenization",
  "entity_extraction",
  "intent_detection",
  "intent_reinforcement",
  "policy_guard",
  "provider_selection",
  "orchestrator",
  "prompt_builder",
  "agent_selection",
  "tool_execution",
  "provider_execution",
  "response_generation",
  "audit_log",
];

function pendingTrace(): TraceStep[] {
  return STAGES.map((stage) => ({
    stage,
    status: "pending",
    input_type: "pending",
    output_type: "pending",
    input: {},
    output: {},
    metadata: {},
  }));
}

function withActiveStage(steps: TraceStep[], activeIndex: number): TraceStep[] {
  return steps.map((step, index) => {
    if (index < activeIndex) {
      return step;
    }
    if (index === activeIndex) {
      return { ...step, status: "active" };
    }
    return { ...step, status: "pending" };
  });
}

function newId() {
  return crypto.randomUUID();
}

function App() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: newId(),
      role: "assistant",
      content: "Demo local listo. El pipeline se visualiza al procesar el primer mensaje.",
    },
  ]);
  const [trace, setTrace] = useState<TraceStep[]>(pendingTrace);
  const [selectedStage, setSelectedStage] = useState<string | null>("raw_input");
  const [response, setResponse] = useState<ChatResponse | null>(null);
  const [rules, setRules] = useState<SecurityRule[]>([]);
  const [attackExamples, setAttackExamples] = useState<AIAttackExample[]>([]);
  const [provider, setProvider] = useState<ProviderName>("local_mock");
  const [providerStatus, setProviderStatus] = useState<ProviderStatus[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const timersRef = useRef<number[]>([]);

  useEffect(() => {
    fetchSecurityRules()
      .then(setRules)
      .catch((err: unknown) => {
        setError(err instanceof Error ? err.message : "No se pudieron cargar las reglas.");
      });
    fetchAIAttackExamples()
      .then(setAttackExamples)
      .catch((err: unknown) => {
        setError(err instanceof Error ? err.message : "No se pudieron cargar los ejemplos de ataques IA.");
      });
    fetchProviderStatus()
      .then(setProviderStatus)
      .catch((err: unknown) => {
        setError(err instanceof Error ? err.message : "No se pudo cargar el estado de proveedores.");
      });

    return () => {
      timersRef.current.forEach(window.clearTimeout);
    };
  }, []);

  const selectedStep = useMemo(() => {
    return trace.find((step) => step.stage === selectedStage) ?? trace[0] ?? null;
  }, [selectedStage, trace]);

  const animateTrace = useCallback((steps: TraceStep[]) => {
    timersRef.current.forEach(window.clearTimeout);
    timersRef.current = [];

    steps.forEach((step, index) => {
      const timer = window.setTimeout(() => {
        setTrace(withActiveStage(steps, index));
        setSelectedStage(step.stage);
      }, index * 420);
      timersRef.current.push(timer);
    });

    const finalTimer = window.setTimeout(() => {
      setTrace(steps);
      setSelectedStage(steps[steps.length - 1]?.stage ?? "audit_log");
      setIsLoading(false);
    }, steps.length * 420 + 120);
    timersRef.current.push(finalTimer);
  }, []);

  async function handleSend(message: string) {
    setError(null);
    setIsLoading(true);
    setResponse(null);
    setTrace(pendingTrace());
    setSelectedStage("raw_input");
    setMessages((current) => [...current, { id: newId(), role: "user", content: message }]);

    try {
      const payload = await sendChatMessage(message, provider);
      setResponse(payload);
      setMessages((current) => [...current, { id: newId(), role: "assistant", content: payload.response }]);
      animateTrace(payload.trace);
    } catch (err) {
      setIsLoading(false);
      setError(err instanceof Error ? err.message : "No se pudo procesar el mensaje.");
    }
  }

  return (
    <main className="app-shell">
      <ChatPanel
        messages={messages}
        isLoading={isLoading}
        error={error}
        provider={provider}
        providerStatus={providerStatus}
        onProviderChange={setProvider}
        onSend={handleSend}
      />
      <section className="center-stack">
        <MetricBar response={response} />
        <FlowPanel trace={trace} selectedStage={selectedStage} onSelectStage={setSelectedStage} />
        <ComputeDashboard response={response} />
      </section>
      <InspectorPanel selectedStep={selectedStep} response={response} rules={rules} attackExamples={attackExamples} />
    </main>
  );
}

export default App;
