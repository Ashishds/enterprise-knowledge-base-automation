import { FileText } from "lucide-react";
import type { Citation } from "@/types";

export function CitationChip({ citation, onSelect }: { citation: Citation; onSelect: (c: Citation) => void }) {
  return (
    <button
      type="button"
      onClick={() => onSelect(citation)}
      className="mono-tag group inline-flex items-center gap-1.5 rounded-xs border border-border bg-secondary px-2 py-0.5 text-[11px] text-secondary-foreground transition-colors hover:border-brand hover:bg-accent"
      title={`${citation.document_name} · similarity ${citation.similarity.toFixed(2)}`}
    >
      <FileText className="h-3 w-3 text-brand" />
      {citation.chunk_id.slice(0, 8)}
    </button>
  );
}
