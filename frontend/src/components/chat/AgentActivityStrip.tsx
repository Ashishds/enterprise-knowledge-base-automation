import { Loader2 } from "lucide-react";

const STAGES = ["Searching documents", "Checking evidence", "Composing answer"];

/** Coarse, whitelisted steps only — never the plan, tool args, or raw tool
 * output (frontend.md §3 / DESIGN-SYSTEM.md §8). */
export function AgentActivityStrip({ stage }: { stage: number }) {
  return (
    <div className="flex items-center gap-2 rounded-lg border border-border bg-secondary/40 px-3 py-2 text-xs text-muted-foreground">
      <Loader2 className="h-3.5 w-3.5 animate-spin text-brand" />
      <span className="animate-pulse-soft">{STAGES[Math.min(stage, STAGES.length - 1)]}…</span>
    </div>
  );
}
