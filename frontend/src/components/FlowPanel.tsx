import { memo, useMemo, useState } from "react";
import {
  Background,
  Controls,
  Handle,
  MarkerType,
  Position,
  ReactFlow,
  type Edge,
  type Node,
  type NodeMouseHandler,
  type NodeProps,
} from "reactflow";
import { Download, Loader2 } from "lucide-react";
import { exportTraceGif } from "../services/exportTraceGif";
import type { TraceStep, TraceStatus } from "../types/api";

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

const STATUS_LABELS: Record<TraceStatus, string> = {
  pending: "pending",
  active: "active",
  completed: "completed",
  blocked: "blocked",
  error: "error",
};

interface FlowPanelProps {
  trace: TraceStep[];
  selectedStage: string | null;
  onSelectStage: (stage: string) => void;
}

type FlowNodeData = {
  label: string;
  status: TraceStatus;
  dataType: string;
  selected: boolean;
};

const FlowNode = memo(({ data }: NodeProps<FlowNodeData>) => (
  <div className={`flow-node status-${data.status} ${data.selected ? "is-selected" : ""}`}>
    <Handle type="target" position={Position.Left} />
    <div className="flow-node-title">{data.label}</div>
    <div className="flow-node-meta">
      <span>{STATUS_LABELS[data.status]}</span>
      <span>{data.dataType}</span>
    </div>
    <Handle type="source" position={Position.Right} />
  </div>
));

FlowNode.displayName = "FlowNode";

const nodeTypes = { flowNode: FlowNode };

export function FlowPanel({ trace, selectedStage, onSelectStage }: FlowPanelProps) {
  const [isExporting, setIsExporting] = useState(false);

  const nodes = useMemo<Node<FlowNodeData>[]>(() => {
    return trace.map((step, index) => {
      const column = index % 3;
      const row = Math.floor(index / 3);
      return {
        id: step.stage,
        type: "flowNode",
        position: { x: column * 250, y: row * 124 },
        data: {
          label: STAGE_LABELS[step.stage] ?? step.stage,
          status: step.status,
          dataType: step.output_type || step.input_type,
          selected: selectedStage === step.stage,
        },
      };
    });
  }, [selectedStage, trace]);

  const edges = useMemo<Edge[]>(() => {
    return trace.slice(0, -1).map((step, index) => {
      const next = trace[index + 1];
      const isAnimated = step.status === "completed" || step.status === "active";
      return {
        id: `${step.stage}-${next.stage}`,
        source: step.stage,
        target: next.stage,
        type: "smoothstep",
        animated: isAnimated,
        markerEnd: { type: MarkerType.ArrowClosed },
        className: isAnimated ? "edge-active" : "edge-muted",
      };
    });
  }, [trace]);

  const handleExportGif = async () => {
    try {
      setIsExporting(true);
      await exportTraceGif(trace);
    } finally {
      setIsExporting(false);
    }
  };

  const handleNodeClick: NodeMouseHandler = (_, node) => {
    onSelectStage(node.id);
  };

  return (
    <section className="panel flow-panel" aria-label="Flujo">
      <header className="panel-header compact">
        <div>
          <p className="eyebrow">Pipeline</p>
          <h2>Flujo interno</h2>
        </div>
        <button
          className="panel-action"
          type="button"
          onClick={handleExportGif}
          disabled={!trace.length || isExporting}
          title="Guardar secuencia del pipeline como GIF"
        >
          {isExporting ? <Loader2 size={16} className="spin-icon" /> : <Download size={16} />}
          <span>{isExporting ? "Generando" : "GIF"}</span>
        </button>
      </header>
      <div className="flow-canvas">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          nodeTypes={nodeTypes}
          fitView
          fitViewOptions={{ padding: 0.12 }}
          minZoom={0.55}
          maxZoom={1.35}
          onNodeClick={handleNodeClick}
          nodesDraggable={false}
          nodesConnectable={false}
          elementsSelectable
        >
          <Background gap={18} size={1} />
          <Controls showInteractive={false} />
        </ReactFlow>
      </div>
    </section>
  );
}
