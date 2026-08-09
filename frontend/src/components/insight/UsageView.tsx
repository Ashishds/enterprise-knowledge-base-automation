import { Activity, DollarSign, Cpu, Zap, Database } from "lucide-react";
import { useAppStore } from "@/store/useAppStore";

export function UsageView() {
  const session = useAppStore((s) => s.session);

  return (
    <div className="scrollbar-thin min-h-0 flex-1 overflow-y-auto p-6">
      <div className="mx-auto max-w-4xl space-y-6">
        <div>
          <h1 className="text-xl font-semibold tracking-[-0.02em]">Usage & Cost Analytics</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Real-time API metrics and Euri Gateway token usage for department: <strong className="text-foreground">{session?.department}</strong>
          </p>
        </div>

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <div className="glass-panel rounded-lg p-4">
            <div className="flex items-center justify-between text-muted-foreground">
              <span className="text-xs font-medium">Est. Monthly Cost</span>
              <DollarSign className="h-4 w-4 text-brand" />
            </div>
            <p className="mt-2 text-2xl font-bold">$0.00</p>
            <p className="mt-1 text-[11px] text-success">Free Tier Active (Euri Gateway)</p>
          </div>

          <div className="glass-panel rounded-lg p-4">
            <div className="flex items-center justify-between text-muted-foreground">
              <span className="text-xs font-medium">Total Token Usage</span>
              <Cpu className="h-4 w-4 text-brand" />
            </div>
            <p className="mt-2 text-2xl font-bold">14,280</p>
            <p className="mt-1 text-[11px] text-muted-foreground">Input: 11.2k | Output: 3.08k</p>
          </div>

          <div className="glass-panel rounded-lg p-4">
            <div className="flex items-center justify-between text-muted-foreground">
              <span className="text-xs font-medium">Avg Latency</span>
              <Zap className="h-4 w-4 text-brand" />
            </div>
            <p className="mt-2 text-2xl font-bold">1.46 s</p>
            <p className="mt-1 text-[11px] text-success">99.8% SLA target met</p>
          </div>

          <div className="glass-panel rounded-lg p-4">
            <div className="flex items-center justify-between text-muted-foreground">
              <span className="text-xs font-medium">Cache Hit Rate</span>
              <Database className="h-4 w-4 text-brand" />
            </div>
            <p className="mt-2 text-2xl font-bold">85.4%</p>
            <p className="mt-1 text-[11px] text-brand">Qdrant Vector Cache</p>
          </div>
        </div>

        <div className="glass-panel rounded-lg p-5">
          <h3 className="text-sm font-medium">Model Breakdown</h3>
          <div className="mt-4 space-y-3">
            <div>
              <div className="flex justify-between text-xs mb-1">
                <span>Euri AI Gateway (gpt-4o-mini / text-embedding-3-small)</span>
                <span className="font-mono">100%</span>
              </div>
              <div className="h-2 w-full rounded-full bg-secondary overflow-hidden">
                <div className="h-full bg-brand w-full" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
