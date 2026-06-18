export type TraceStatus = "pending" | "active" | "completed" | "blocked" | "error";
export type ProviderName = "local_mock" | "openai_api";

export interface TraceStep {
  stage: string;
  status: TraceStatus;
  input_type: string;
  output_type: string;
  input: Record<string, unknown>;
  output: Record<string, unknown>;
  metadata: Record<string, unknown>;
}

export interface TokenUsage {
  input_tokens: number;
  output_tokens: number;
  total_tokens: number;
}

export interface ComputeMetrics {
  provider: ProviderName;
  model: string;
  latency_ms: number;
  estimated_cpu_ms: number;
  estimated_ram_mb: number;
  estimated_context_tokens: number;
  input_tokens: number;
  output_tokens: number;
  total_tokens: number;
  estimated_cost_usd: number;
  mode_note: string;
}

export interface ProviderSummary {
  requested_provider: ProviderName;
  selected_provider: ProviderName;
  model: string;
  available: boolean;
  reason: string;
}

export interface SecuritySummary {
  allowed: boolean;
  triggered_rules: string[];
}

export interface IntentReinforcementSummary {
  enabled: boolean;
  provider: string;
  original_intent: string;
  final_intent: string;
  changed: boolean;
  confidence: number;
  signals: string[];
  rationale: string;
}

export interface ChatResponse {
  response: string;
  trace: TraceStep[];
  token_usage: TokenUsage;
  security: SecuritySummary;
  provider: ProviderSummary;
  compute: ComputeMetrics;
  intent_reinforcement: IntentReinforcementSummary;
  intent: string;
  agent: string;
  tool: string | null;
  estimated_cost_usd: number;
}

export interface SecurityRule {
  id: string;
  title: string;
  description: string;
  severity: "low" | "medium" | "high";
  category: string;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
}

export interface AIAttackExample {
  id: string;
  title: string;
  category: string;
  sample_instruction: string;
  risk: string;
  expected_defense: string;
  related_rules: string[];
}

export interface ProviderStatus {
  provider: ProviderName;
  available: boolean;
  model: string;
  reason: string;
  requires_api_key: boolean;
  exposes_secret_to_frontend: boolean;
}
