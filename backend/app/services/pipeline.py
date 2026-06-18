from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4

from app.agents.base import AgentContext
from app.agents.registry import get_agent, list_agents
from app.schemas import (
    ChatResponse,
    ComputeMetrics,
    IntentReinforcementSummary,
    ProviderSummary,
    SecuritySummary,
    TokenUsage,
    TraceStep,
)
from app.services.intent_detector import detect_intent
from app.services.observability import estimate_local_compute, estimate_openai_compute
from app.services.openia_intent_reinforcer import reinforce_intent
from app.services.orchestrator import create_plan
from app.services.policy_guard import evaluate_policy
from app.services.prompt_builder import build_prompt
from app.services.provider_selection import select_provider
from app.services.sanitizer import safe_preview, sanitize_payload
from app.services.text_processing import estimate_tokens, extract_entities, normalize_text, tokenize
from app.tools.registry import execute_tool, list_allowed_tools


PIPELINE_STAGES = [
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
]


def make_trace(
    stage: str,
    status: str,
    input_type: str,
    output_type: str,
    input_payload: dict[str, Any],
    output_payload: dict[str, Any],
    metadata: Optional[dict[str, Any]] = None,
) -> TraceStep:
    return TraceStep(
        stage=stage,
        status=status,  # type: ignore[arg-type]
        input_type=input_type,
        output_type=output_type,
        input=sanitize_payload(input_payload),
        output=sanitize_payload(output_payload),
        metadata=sanitize_payload(metadata or {}),
    )


def _blocked_trace(stage: str, reason: str) -> TraceStep:
    return make_trace(
        stage=stage,
        status="blocked",
        input_type="blocked",
        output_type="blocked",
        input_payload={},
        output_payload={"skipped": True, "reason": reason},
    )


def _provider_summary(decision) -> ProviderSummary:
    return ProviderSummary(
        requested_provider=decision.requested_provider,
        selected_provider=decision.selected_provider,
        model=decision.model,
        available=decision.available,
        reason=decision.reason,
    )


def _reinforcement_summary(reinforcement) -> IntentReinforcementSummary:
    return IntentReinforcementSummary(
        enabled=reinforcement.enabled,
        provider=reinforcement.provider,
        original_intent=reinforcement.original_intent,
        final_intent=reinforcement.final_intent,
        changed=reinforcement.changed,
        confidence=reinforcement.confidence,
        signals=reinforcement.signals,
        rationale=reinforcement.rationale,
    )


def _compute_metrics(payload: dict[str, object]) -> ComputeMetrics:
    return ComputeMetrics(**payload)


def process_chat_message(message: str, provider: str = "local_mock") -> ChatResponse:
    trace: list[TraceStep] = []

    trace.append(
        make_trace(
            "raw_input",
            "completed",
            "ChatRequest",
            "RawMessage",
            {},
            {"message_preview": safe_preview(message), "char_count": len(message)},
            {"max_message_length": 1000},
        )
    )

    normalized = normalize_text(message)
    trace.append(
        make_trace(
            "normalization",
            "completed",
            "RawMessage",
            "NormalizedText",
            {"message_preview": safe_preview(message)},
            {"normalized_text": normalized},
            {"transformation": "trim + whitespace collapse + lowercase"},
        )
    )

    tokens = tokenize(normalized)
    input_tokens = estimate_tokens(message)
    trace.append(
        make_trace(
            "tokenization",
            "completed",
            "NormalizedText",
            "TokenList",
            {"normalized_text": normalized},
            {"tokens": tokens[:40], "token_count": len(tokens), "estimated_tokens": input_tokens},
            {"estimator": "regex tokens plus chars/4 heuristic"},
        )
    )

    entities = extract_entities(message)
    trace.append(
        make_trace(
            "entity_extraction",
            "completed",
            "NormalizedText",
            "EntityList",
            {"normalized_text": normalized},
            {"entities": entities},
            {"extractors": ["url", "email", "technology_keyword", "repeated_terms"]},
        )
    )

    intent_result = detect_intent(normalized)
    trace.append(
        make_trace(
            "intent_detection",
            "completed",
            "NormalizedText + EntityList",
            "IntentResult",
            {"normalized_text": normalized, "entities": entities},
            {
                "intent": intent_result.intent,
                "confidence": intent_result.confidence,
                "matched_keywords": intent_result.matched_keywords,
            },
            {"strategy": "keyword rules"},
        )
    )

    reinforcement = reinforce_intent(normalized, entities, intent_result)
    final_intent = reinforcement.final_intent
    trace.append(
        make_trace(
            "intent_reinforcement",
            "completed" if reinforcement.enabled else "blocked",
            "IntentResult + EntityList",
            "IntentReinforcementResult",
            {
                "base_intent": intent_result.intent,
                "base_confidence": intent_result.confidence,
                "entities": entities,
            },
            {
                "provider": reinforcement.provider,
                "enabled": reinforcement.enabled,
                "original_intent": reinforcement.original_intent,
                "final_intent": reinforcement.final_intent,
                "changed": reinforcement.changed,
                "confidence": reinforcement.confidence,
                "signals": reinforcement.signals,
                "rationale": reinforcement.rationale,
            },
            {"mode": "offline by default", "external_api_calls": False},
        )
    )

    policy = evaluate_policy(message, input_tokens)
    trace.append(
        make_trace(
            "policy_guard",
            "completed" if policy.allowed else "blocked",
            "IntentResult + TokenBudget",
            "PolicyDecision",
            {"intent": final_intent, "input_tokens": input_tokens},
            {
                "allowed": policy.allowed,
                "triggered_rules": policy.triggered_rules,
                "reason": policy.reason,
            },
            {"mode": "fail_closed"},
        )
    )

    provider_decision = select_provider(provider)
    trace.append(
        make_trace(
            "provider_selection",
            "completed" if provider_decision.available else "blocked",
            "ProviderRequest + PolicyDecision",
            "ProviderDecision",
            {"requested_provider": provider, "security_allowed": policy.allowed},
            {
                "requested_provider": provider_decision.requested_provider,
                "selected_provider": provider_decision.selected_provider,
                "model": provider_decision.model,
                "available": provider_decision.available,
                "reason": provider_decision.reason,
            },
            {"fallback_allowed": True, "frontend_secret_exposure": False},
        )
    )

    if not policy.allowed:
        blocked_reason = policy.reason
        for stage in ["orchestrator", "prompt_builder", "agent_selection", "tool_execution", "provider_execution", "response_generation"]:
            trace.append(_blocked_trace(stage, blocked_reason))

        response = "No puedo procesar ese mensaje porque activo una politica de seguridad local. Reformula la solicitud sin instrucciones de bypass, secretos ni exceso de contexto."
        output_tokens = estimate_tokens(response)
        compute = estimate_local_compute(input_tokens, output_tokens, input_tokens)
        trace.append(
            make_trace(
                "audit_log",
                "completed",
                "PolicyDecision",
                "AuditEvent",
                {"allowed": False},
                {
                    "event_id": str(uuid4()),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "result": "blocked",
                    "triggered_rules": policy.triggered_rules,
                },
                {"secrets_redacted": True},
            )
        )
        return ChatResponse(
            response=response,
            trace=trace,
            token_usage=TokenUsage(input_tokens=input_tokens, output_tokens=output_tokens, total_tokens=input_tokens + output_tokens),
            security=SecuritySummary(allowed=False, triggered_rules=policy.triggered_rules),
            provider=_provider_summary(provider_decision),
            compute=_compute_metrics(compute),
            intent_reinforcement=_reinforcement_summary(reinforcement),
            intent=final_intent,
            agent="None",
            tool=None,
            estimated_cost_usd=0.0,
        )

    plan = create_plan(final_intent)
    trace.append(
        make_trace(
            "orchestrator",
            "completed",
            "IntentResult + PolicyDecision",
            "OrchestrationPlan",
            {"intent": final_intent, "allowed": policy.allowed, "provider": provider_decision.selected_provider},
            {
                "intent": plan.intent,
                "agent_name": plan.agent_name,
                "tool_name": plan.tool_name,
                "rationale": plan.rationale,
            },
            {"available_agents": list_agents()},
        )
    )

    agent = get_agent(plan.agent_name)
    prompt_result = build_prompt(
        user_message=message,
        intent=final_intent,
        agent_name=agent.name,
        provider=provider_decision.selected_provider,
        tool_output=None,
    )
    trace.append(
        make_trace(
            "prompt_builder",
            "completed",
            "OrchestrationPlan + UserMessage",
            "PromptBuildResult",
            {"intent": final_intent, "agent_name": agent.name, "provider": provider_decision.selected_provider},
            {
                "system_prompt": prompt_result.system_prompt,
                "developer_policy": prompt_result.developer_policy,
                "conversation_history": prompt_result.conversation_history,
                "retrieved_context": prompt_result.retrieved_context,
                "tool_results": prompt_result.tool_results,
                "user_message": prompt_result.user_message,
                "final_prompt_preview": prompt_result.final_prompt_preview,
                "estimated_input_tokens": prompt_result.estimated_input_tokens,
            },
            {"purpose": "Expose how the final LLM prompt would be assembled."},
        )
    )

    trace.append(
        make_trace(
            "agent_selection",
            "completed",
            "OrchestrationPlan",
            "AgentDescriptor",
            {"agent_name": plan.agent_name},
            {"name": agent.name, "description": agent.description},
            {"selection_rule": "intent_to_agent_map"},
        )
    )

    tool_output: Optional[dict[str, Any]] = None
    if plan.tool_name:
        tool_output = execute_tool(plan.tool_name, message)
    prompt_result = build_prompt(
        user_message=message,
        intent=final_intent,
        agent_name=agent.name,
        provider=provider_decision.selected_provider,
        tool_output=tool_output,
    )
    trace.append(
        make_trace(
            "tool_execution",
            "completed",
            "ToolInvocation",
            "ToolResult",
            {"tool_name": plan.tool_name, "allowlist": list_allowed_tools()},
            {"executed": bool(plan.tool_name), "tool_name": plan.tool_name, "result": tool_output},
            {"execution": "local deterministic function"},
        )
    )

    provider_execution_status = "completed"
    provider_execution_note = "Local deterministic provider executed in-process."
    if provider_decision.selected_provider == "openai_api":
        provider_execution_note = (
            "OpenAI API provider selected for architecture demonstration. Live SDK execution is intentionally "
            "not enabled until credentials and adapter activation are confirmed."
        )
    trace.append(
        make_trace(
            "provider_execution",
            provider_execution_status,
            "PromptBuildResult + ProviderDecision",
            "ProviderExecutionResult",
            {
                "provider": provider_decision.selected_provider,
                "model": provider_decision.model,
                "estimated_input_tokens": prompt_result.estimated_input_tokens,
            },
            {
                "executed_live_call": False,
                "provider": provider_decision.selected_provider,
                "model": provider_decision.model,
                "note": provider_execution_note,
            },
            {"backend_only": True, "api_key_exposed": False},
        )
    )

    context = AgentContext(
        intent=final_intent,
        input_tokens=input_tokens,
        entities=entities,
        normalized_text=normalized,
    )
    response = agent.respond(context, tool_output)
    output_tokens = estimate_tokens(response)
    if provider_decision.selected_provider == "openai_api":
        compute = estimate_openai_compute(provider_decision.model, prompt_result.estimated_input_tokens, output_tokens, prompt_result.estimated_input_tokens)
    else:
        compute = estimate_local_compute(prompt_result.estimated_input_tokens, output_tokens, prompt_result.estimated_input_tokens)
    trace.append(
        make_trace(
            "response_generation",
            "completed",
            "AgentContext + ToolResult",
            "AssistantMessage",
            {"agent_name": agent.name, "tool_name": plan.tool_name},
            {"response_preview": safe_preview(response), "output_tokens": output_tokens, "provider": provider_decision.selected_provider},
            {"generation": "template-based local response", "provider_execution": provider_execution_note},
        )
    )

    trace.append(
        make_trace(
            "audit_log",
            "completed",
            "ChatTransaction",
            "AuditEvent",
            {"intent": final_intent, "agent": agent.name, "tool": plan.tool_name},
            {
                "event_id": str(uuid4()),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "result": "completed",
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "latency_ms": compute["latency_ms"],
                "provider": provider_decision.selected_provider,
                "security_allowed": policy.allowed,
            },
            {"secrets_redacted": True, "retention": "in-memory response only"},
        )
    )

    return ChatResponse(
        response=response,
        trace=trace,
        token_usage=TokenUsage(
            input_tokens=prompt_result.estimated_input_tokens,
            output_tokens=output_tokens,
            total_tokens=prompt_result.estimated_input_tokens + output_tokens,
        ),
        security=SecuritySummary(allowed=True, triggered_rules=policy.triggered_rules),
        provider=_provider_summary(provider_decision),
        compute=_compute_metrics(compute),
        intent_reinforcement=_reinforcement_summary(reinforcement),
        intent=final_intent,
        agent=agent.name,
        tool=plan.tool_name,
        estimated_cost_usd=float(compute["estimated_cost_usd"]),
    )
