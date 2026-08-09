import { useEffect, useRef, useState } from "react";
import { MessageSquareText } from "lucide-react";
import { api, ApiError } from "@/lib/api";
import { useAppStore } from "@/store/useAppStore";
import type { Citation, DisplayMessage } from "@/types";
import { MessageBubble } from "@/components/chat/MessageBubble";
import { Composer } from "@/components/chat/Composer";
import { AgentActivityStrip } from "@/components/chat/AgentActivityStrip";
import { CitationPanel } from "@/components/chat/CitationPanel";

let idCounter = 0;
const nextId = () => `msg-${++idCounter}-${Date.now()}`;

export function ChatWindow() {
  const session = useAppStore((s) => s.session);
  const [messages, setMessages] = useState<DisplayMessage[]>([]);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeCitations, setActiveCitations] = useState<Citation[]>([]);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, pending]);

  const send = async (text: string) => {
    if (!session) return;
    setError(null);
    const userMsg: DisplayMessage = { id: nextId(), role: "user", content: text };
    const history = messages.map(({ role, content }) => ({ role, content }));
    setMessages((prev) => [...prev, userMsg]);
    setPending(true);

    try {
      const res = await api.chat(text, session.department, history);
      const assistantMsg: DisplayMessage = {
        id: nextId(),
        role: "assistant",
        content: res.answer,
        citations: res.citations,
        refusal: res.refusal,
        meta: {
          model_used: res.model_used,
          input_tokens: res.input_tokens,
          output_tokens: res.output_tokens,
          estimated_cost_usd: res.estimated_cost_usd,
          latency_ms: res.latency_ms,
          cache_hit: res.cache_hit,
          trace_id: res.trace_id,
          confidence: res.confidence,
        },
      };
      setMessages((prev) => [...prev, assistantMsg]);
      if (res.citations.length > 0) setActiveCitations(res.citations);
    } catch (err) {
      const message = err instanceof ApiError ? err.message : "Could not reach the EKBA API.";
      setError(message);
    } finally {
      setPending(false);
    }
  };

  return (
    <div className="flex min-h-0 flex-1">
      <div className="flex min-h-0 flex-1 flex-col">
        <div ref={scrollRef} className="scrollbar-thin min-h-0 flex-1 overflow-y-auto px-4 py-6 sm:px-6">
          <div className="mx-auto flex max-w-[36rem] flex-col gap-6">
            {messages.length === 0 && (
              <div className="animate-fade-up mt-10 flex flex-col items-center gap-3 text-center text-muted-foreground">
                <span className="flex h-12 w-12 items-center justify-center rounded-full bg-accent text-brand">
                  <MessageSquareText className="h-5 w-5" />
                </span>
                <p className="max-w-xs text-sm">
                  Ask a question about a document in <strong className="text-foreground">{session?.department}</strong>.
                  Try uploading one first from the Documents panel.
                </p>
              </div>
            )}

            {messages.map((m) => (
              <MessageBubble key={m.id} message={m} onRephrase={send} onSelectCitation={(c) => setActiveCitations([c])} />
            ))}

            {pending && <AgentActivityStrip stage={messages.length % 3} />}

            {error && (
              <div className="rounded-lg border border-danger/40 bg-danger/10 px-4 py-3 text-sm text-danger">{error}</div>
            )}
          </div>
        </div>

        <div className="mx-auto w-full max-w-[36rem] px-4 sm:px-0">
          <Composer onSend={send} disabled={pending} />
        </div>
      </div>

      {activeCitations.length > 0 && (
        <CitationPanel citations={activeCitations} onClose={() => setActiveCitations([])} />
      )}
    </div>
  );
}
