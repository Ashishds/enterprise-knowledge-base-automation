import { Info } from "lucide-react";

export function RefusalCard({ message, onRephrase }: { message: string; onRephrase: () => void }) {
  return (
    <div className="flex gap-3 rounded-lg border border-neutral/40 bg-secondary/40 p-4">
      <span className="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-neutral/15 text-neutral">
        <Info className="h-3.5 w-3.5" />
      </span>
      <div className="flex-1">
        <p className="text-sm text-foreground/90">{message}</p>
        <div className="mt-3 flex gap-2">
          <button
            type="button"
            onClick={onRephrase}
            className="rounded border border-border bg-card px-3 py-1.5 text-xs font-medium transition-colors hover:bg-accent"
          >
            Rephrase
          </button>
          <button
            type="button"
            className="rounded border border-border bg-card px-3 py-1.5 text-xs font-medium transition-colors hover:bg-accent"
          >
            Request access
          </button>
        </div>
      </div>
    </div>
  );
}
