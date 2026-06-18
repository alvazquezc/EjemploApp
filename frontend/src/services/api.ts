import type { AIAttackExample, ChatResponse, ProviderName, ProviderStatus, SecurityRule } from "../types/api";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

async function requestJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
  });

  if (!response.ok) {
    const fallback = `Request failed with status ${response.status}`;
    let message = fallback;
    try {
      const errorPayload = (await response.json()) as { detail?: unknown };
      message = typeof errorPayload.detail === "string" ? errorPayload.detail : fallback;
    } catch {
      message = fallback;
    }
    throw new Error(message);
  }

  return response.json() as Promise<T>;
}

export function sendChatMessage(message: string, provider: ProviderName): Promise<ChatResponse> {
  return requestJson<ChatResponse>("/api/chat", {
    method: "POST",
    body: JSON.stringify({ message, provider }),
  });
}

export async function fetchSecurityRules(): Promise<SecurityRule[]> {
  const payload = await requestJson<{ rules: SecurityRule[] }>("/api/security-rules");
  return payload.rules;
}

export async function fetchAIAttackExamples(): Promise<AIAttackExample[]> {
  const payload = await requestJson<{ examples: AIAttackExample[] }>("/api/ai-attack-examples");
  return payload.examples;
}

export async function fetchProviderStatus(): Promise<ProviderStatus[]> {
  const payload = await requestJson<{ providers: ProviderStatus[] }>("/api/provider-status");
  return payload.providers;
}
