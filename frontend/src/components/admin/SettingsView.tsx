import { useState } from "react";
import { Sliders, CheckCircle2, ShieldAlert } from "lucide-react";
import { useAppStore } from "@/store/useAppStore";

export function SettingsView() {
  const session = useAppStore((s) => s.session);
  const [topK, setTopK] = useState(3);
  const [confidence, setConfidence] = useState(0.7);
  const [saved, setSaved] = useState(false);

  const save = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <div className="scrollbar-thin min-h-0 flex-1 overflow-y-auto p-6">
      <div className="mx-auto max-w-2xl space-y-6">
        <div>
          <h1 className="text-xl font-semibold tracking-[-0.02em]">System Settings</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Configure RAG pipeline parameters, refusal strictness, and retrieval parameters.
          </p>
        </div>

        {saved && (
          <div className="flex items-center gap-2 rounded bg-success/10 border border-success/30 px-4 py-3 text-xs text-success">
            <CheckCircle2 className="h-4 w-4" />
            Settings saved successfully.
          </div>
        )}

        <div className="glass-panel rounded-lg p-6 space-y-6">
          <div className="flex items-center gap-2 pb-4 border-b border-border">
            <Sliders className="h-5 w-5 text-brand" />
            <h3 className="text-sm font-medium">Retrieval & Refusal Parameters</h3>
          </div>

          <div className="space-y-4">
            <div>
              <label className="text-xs font-medium text-muted-foreground flex justify-between">
                <span>Top-K Chunks Retrieved ({topK})</span>
                <span>Default: 3</span>
              </label>
              <input
                type="range"
                min={1}
                max={10}
                value={topK}
                onChange={(e) => setTopK(Number(e.target.value))}
                className="w-full mt-2 accent-brand"
              />
            </div>

            <div>
              <label className="text-xs font-medium text-muted-foreground flex justify-between">
                <span>Refusal Grounding Score Threshold ({confidence})</span>
                <span>Default: 0.70</span>
              </label>
              <input
                type="range"
                min={0.5}
                max={0.95}
                step={0.05}
                value={confidence}
                onChange={(e) => setConfidence(Number(e.target.value))}
                className="w-full mt-2 accent-brand"
              />
              <p className="mt-1 text-[11px] text-muted-foreground">
                Queries below score {confidence} will output strict refusal string <code className="text-foreground">INSUFFICIENT_EVIDENCE</code>.
              </p>
            </div>
          </div>

          <div className="pt-4 border-t border-border flex justify-end">
            <button
              onClick={save}
              className="rounded bg-brand px-4 py-2 text-xs font-medium text-brand-foreground shadow hover:scale-[1.02] active:scale-[0.98]"
            >
              Save Configuration
            </button>
          </div>
        </div>

        <div className="glass-panel rounded-lg p-5 border border-brand/20">
          <div className="flex items-center gap-2 mb-2 text-xs font-medium">
            <ShieldAlert className="h-4 w-4 text-brand" />
            Zero-Hallucination Operating Mode
          </div>
          <p className="text-xs text-muted-foreground">
            Strict grounded answer synthesis is enforced on all department queries. Synthetic content generation without evidence is automatically refused.
          </p>
        </div>
      </div>
    </div>
  );
}
