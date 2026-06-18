from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator
from typing_extensions import Literal


MAX_MESSAGE_LENGTH = 1000

TraceStatus = Literal["pending", "active", "completed", "blocked", "error"]
ProviderName = Literal["local_mock", "openai_api"]


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=MAX_MESSAGE_LENGTH)
    provider: ProviderName = "local_mock"

    @validator("message")
    @classmethod
    def message_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("El mensaje no puede estar vacio.")
        return value


class TraceStep(BaseModel):
    stage: str
    status: TraceStatus
    input_type: str
    output_type: str
    input: Dict[str, Any] = Field(default_factory=dict)
    output: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TokenUsage(BaseModel):
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0


class ComputeMetrics(BaseModel):
    provider: ProviderName
    model: str
    latency_ms: int = 0
    estimated_cpu_ms: int = 0
    estimated_ram_mb: int = 0
    estimated_context_tokens: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    estimated_cost_usd: float = 0.0
    mode_note: str


class ProviderSummary(BaseModel):
    requested_provider: ProviderName
    selected_provider: ProviderName
    model: str
    available: bool
    reason: str


class SecuritySummary(BaseModel):
    allowed: bool = True
    triggered_rules: List[str] = Field(default_factory=list)


class IntentReinforcementSummary(BaseModel):
    enabled: bool = True
    provider: str
    original_intent: str
    final_intent: str
    changed: bool = False
    confidence: float = 0.0
    signals: List[str] = Field(default_factory=list)
    rationale: str


class ChatResponse(BaseModel):
    response: str
    trace: List[TraceStep]
    token_usage: TokenUsage
    security: SecuritySummary
    provider: ProviderSummary
    compute: ComputeMetrics
    intent_reinforcement: IntentReinforcementSummary
    intent: str
    agent: str
    tool: Optional[str] = None
    estimated_cost_usd: float = 0.0


class HealthResponse(BaseModel):
    status: Literal["ok"]
    service: str
    version: str


class SecurityRule(BaseModel):
    id: str
    title: str
    description: str
    severity: Literal["low", "medium", "high"]
    category: str


class SecurityRulesResponse(BaseModel):
    rules: List[SecurityRule]


class ProviderStatus(BaseModel):
    provider: ProviderName
    available: bool
    model: str
    reason: str
    requires_api_key: bool
    exposes_secret_to_frontend: bool = False


class ProviderStatusResponse(BaseModel):
    providers: List[ProviderStatus]


class AIAttackExample(BaseModel):
    id: str
    title: str
    category: str
    sample_instruction: str
    risk: str
    expected_defense: str
    related_rules: List[str] = Field(default_factory=list)


class AIAttackExamplesResponse(BaseModel):
    examples: List[AIAttackExample]
