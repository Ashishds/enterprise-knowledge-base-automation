import { FileText } from "lucide-react";
import type { DocumentSummary } from "@/types";
import { timeAgo } from "@/lib/utils";

export function DocumentList({ documents, loading }: { documents: DocumentSummary[]; loading: boolean }) {
  if (loading) {
    return <p className="text-sm text-muted-foreground">Loading documents…</p>;
  }

  if (documents.length === 0) {
    return (
      <p className="rounded-lg border border-border bg-secondary/30 px-4 py-6 text-center text-sm text-muted-foreground">
        No documents indexed for this department yet.
      </p>
    );
  }

  return (
    <ul className="space-y-2">
      {documents.map((doc) => (
        <li key={doc.id} className="flex items-center gap-3 rounded-lg border border-border bg-card px-4 py-3 shadow-sm">
          <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded bg-accent text-brand">
            <FileText className="h-4 w-4" />
          </span>
          <div className="min-w-0 flex-1">
            <p className="truncate text-sm font-medium">{doc.filename}</p>
            <p className="mono-tag text-[11px] text-muted-foreground">
              {doc.chunk_count} chunks · {(doc.char_count / 1000).toFixed(1)}k chars · {timeAgo(doc.created_at)}
            </p>
          </div>
          <span className="rounded-full border border-success/40 bg-success/10 px-2 py-0.5 text-[11px] text-success">
            completed
          </span>
        </li>
      ))}
    </ul>
  );
}
