import { FileText, X } from "lucide-react";
import type { Citation } from "@/types";

export function CitationPanel({ citations, onClose }: { citations: Citation[]; onClose: () => void }) {
  if (citations.length === 0) return null;

  const grouped = citations.reduce<Record<string, Citation[]>>((acc, c) => {
    (acc[c.document_name] ??= []).push(c);
    return acc;
  }, {});

  return (
    <aside className="scrollbar-thin hidden w-96 shrink-0 overflow-y-auto border-l border-border bg-card p-5 xl:w-[28rem] lg:block">
      <div className="mb-4 flex items-center justify-between">
        <h3 className="text-sm font-semibold">Sources</h3>
        <button onClick={onClose} className="rounded p-1 text-muted-foreground hover:bg-accent" aria-label="Close citation panel">
          <X className="h-4 w-4" />
        </button>
      </div>

      <div className="space-y-5">
        {Object.entries(grouped).map(([doc, items]) => (
          <div key={doc}>
            <div className="flex items-center gap-2 text-sm font-medium">
              <FileText className="h-4 w-4 text-brand" />
              {doc}
            </div>
            <div className="mt-2 space-y-2">
              {items.map((c) => (
                <div key={c.chunk_id} className="rounded border border-border bg-secondary/50 p-3">
                  <div className="mono-tag flex items-center justify-between text-[11px] text-muted-foreground">
                    <span>{c.chunk_id.slice(0, 8)}</span>
                    <span>relevance {(c.similarity * 100).toFixed(0)}%</span>
                  </div>
                  <p className="mt-1.5 text-xs leading-relaxed text-foreground/85">{c.snippet}…</p>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </aside>
  );
}
