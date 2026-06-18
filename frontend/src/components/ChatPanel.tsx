import { FormEvent, useState } from "react";
import { AlertTriangle, SendHorizonal } from "lucide-react";
import type { ChatMessage, ProviderName, ProviderStatus } from "../types/api";

interface ChatPanelProps {
  messages: ChatMessage[];
  isLoading: boolean;
  error: string | null;
  provider: ProviderName;
  providerStatus: ProviderStatus[];
  onProviderChange: (provider: ProviderName) => void;
  onSend: (message: string) => void;
}

export function ChatPanel({
  messages,
  isLoading,
  error,
  provider,
  providerStatus,
  onProviderChange,
  onSend,
}: ChatPanelProps) {
  const [draft, setDraft] = useState("");
  const selectedProvider = providerStatus.find((item) => item.provider === provider);

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmed = draft.trim();
    if (!trimmed || isLoading) {
      return;
    }
    onSend(trimmed);
    setDraft("");
  }

  return (
    <section className="panel chat-panel" aria-label="Chat">
      <header className="panel-header">
        <div>
          <p className="eyebrow">Entrada</p>
          <h1>Chatbot Orquestador</h1>
        </div>
      </header>

      <div className="provider-selector">
        <label htmlFor="provider">Modo</label>
        <select
          id="provider"
          value={provider}
          onChange={(event) => onProviderChange(event.target.value as ProviderName)}
          disabled={isLoading}
        >
          <option value="local_mock">Local / Simulado</option>
          <option value="openai_api">OpenAI API</option>
        </select>
        <span>{selectedProvider?.reason ?? "Selecciona un proveedor para la siguiente ejecucion."}</span>
      </div>

      <div className="message-list">
        {messages.map((message) => (
          <article className={`message message-${message.role}`} key={message.id}>
            <span className="message-role">{message.role}</span>
            <p>{message.content}</p>
          </article>
        ))}
        {error ? (
          <article className="message message-system">
            <span className="message-role">
              <AlertTriangle size={14} />
              error
            </span>
            <p>{error}</p>
          </article>
        ) : null}
      </div>

      <form className="composer" onSubmit={handleSubmit}>
        <textarea
          value={draft}
          onChange={(event) => setDraft(event.target.value)}
          maxLength={1000}
          placeholder="Escribe un mensaje"
          disabled={isLoading}
        />
        <div className="composer-actions">
          <span>{draft.length}/1000</span>
          <button type="submit" disabled={isLoading || !draft.trim()} title="Enviar">
            <SendHorizonal size={18} />
          </button>
        </div>
      </form>
    </section>
  );
}
