from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.schemas import (
    AIAttackExamplesResponse,
    ChatRequest,
    ChatResponse,
    HealthResponse,
    ProviderStatusResponse,
    SecurityRulesResponse,
)
from app.services.ai_attack_examples import list_ai_attack_examples
from app.services.pipeline import process_chat_message
from app.services.provider_selection import provider_status
from app.services.security_rules import load_security_rules


app = FastAPI(
    title="Chatbot Orchestrator Flow Demo",
    version="1.0.0",
    description="Demo educativo local para visualizar un pipeline de chatbot con agentes, reglas y tokens.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/api/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", service="chatbot-flow-demo", version=app.version)


@app.get("/api/security-rules", response_model=SecurityRulesResponse)
def security_rules() -> SecurityRulesResponse:
    return SecurityRulesResponse(rules=load_security_rules())


@app.get("/api/provider-status", response_model=ProviderStatusResponse)
def provider_status_endpoint() -> ProviderStatusResponse:
    return ProviderStatusResponse(providers=provider_status())


@app.get("/api/ai-attack-examples", response_model=AIAttackExamplesResponse)
def ai_attack_examples() -> AIAttackExamplesResponse:
    return AIAttackExamplesResponse(examples=list_ai_attack_examples())


@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    return process_chat_message(request.message, provider=request.provider)
