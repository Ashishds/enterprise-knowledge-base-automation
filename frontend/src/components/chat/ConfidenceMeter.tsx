import { cn } from "@/lib/utils";

export function ConfidenceMeter({ value }: { value: number }) {
  const pct = Math.round(value * 100);
  const band = pct >= 66 ? "bg-success" : pct >= 33 ? "bg-warning" : "bg-danger";

  return (
    <div className="flex items-center gap-2">
      <div className="h-1.5 w-16 overflow-hidden rounded-full bg-secondary" role="img" aria-label={`Confidence ${pct}%`}>
        <div className={cn("h-full rounded-full transition-all", band)} style={{ width: `${pct}%` }} />
      </div>
      <span className="mono-tag text-[11px] text-muted-foreground">{pct}%</span>
    </div>
  );
}
