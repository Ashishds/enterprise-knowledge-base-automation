import { Copy } from "lucide-react";
import { formatCost } from "@/lib/utils";
import type { DisplayMessage } from "@/types";
import { ConfidenceMeter } from "@/components/chat/ConfidenceMeter";

export function ResponseMetaRow({ meta }: { meta: NonNullable<DisplayMessage["meta"]> }) {
  return (
    <div className="mono-tag mt-2 flex flex-wrap items-center gap-x-4 gap-y-1.5 text-[11px] text-muted-foreground">
      <span>{meta.model_used}</span>
      <span>{meta.latency_ms}ms</span>
      <span>
        {meta.input_tokens}→{meta.output_tokens} tok
      </span>
      <span>{formatCost(meta.estimated_cost_usd)}</span>
      {meta.cache_hit && (
        <span className="rounded-full border border-info/40 bg-info/10 px-1.5 py-0.5 text-info">cache hit</span>
      )}
      <ConfidenceMeter value={meta.confidence} />
      <button
        type="button"
        onClick={() => navigator.clipboard.writeText(meta.trace_id)}
        className="inline-flex items-center gap-1 transition-colors hover:text-foreground"
        title="Copy trace id"
      >
        <Copy className="h-3 w-3" />
        {meta.trace_id.slice(0, 8)}
      </button>
    </div>
  );
}
