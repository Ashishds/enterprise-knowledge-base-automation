import { useRef, useState } from "react";
import { SendHorizontal } from "lucide-react";

export function Composer({ onSend, disabled }: { onSend: (text: string) => void; disabled: boolean }) {
  const [value, setValue] = useState("");
  const ref = useRef<HTMLTextAreaElement>(null);

  const submit = () => {
    const trimmed = value.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setValue("");
    requestAnimationFrame(() => ref.current?.focus());
  };

  return (
    <div className="border-t border-border bg-card p-3 pb-[max(0.75rem,env(safe-area-inset-bottom))] sm:p-4">
      <div className="flex items-end gap-2 rounded-lg border border-input bg-background px-3 py-2 shadow-sm focus-within:ring-2 focus-within:ring-brand">
        <textarea
          ref={ref}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              submit();
            }
          }}
          rows={1}
          placeholder="Ask about a policy, SOP, or record in your department…"
          aria-label="Message"
          className="max-h-40 flex-1 resize-none bg-transparent text-sm placeholder:text-muted-foreground focus:outline-none"
        />
        <button
          type="button"
          onClick={submit}
          disabled={disabled || !value.trim()}
          aria-label="Send message"
          className="flex h-9 w-9 shrink-0 items-center justify-center rounded bg-brand text-brand-foreground transition-transform enabled:hover:scale-105 disabled:opacity-40"
        >
          <SendHorizontal className="h-4 w-4" />
        </button>
      </div>
      <p className="mt-1.5 text-center text-[11px] text-muted-foreground">
        Answers are grounded in documents scoped to your department, with citations or an explicit refusal.
      </p>
    </div>
  );
}
