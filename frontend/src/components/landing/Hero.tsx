import { Link } from "react-router-dom";
import { ArrowRight, FileCheck2, Globe2, ShieldCheck } from "lucide-react";

export function Hero() {
  return (
    <section className="relative overflow-hidden">
      <div aria-hidden className="brand-glow pointer-events-none absolute inset-x-0 top-0 h-[36rem]" />

      <div className="container relative flex flex-col items-center px-6 pb-20 pt-24 text-center sm:pt-32">
        <span className="mono-tag animate-fade-up inline-flex items-center gap-2 rounded-full border border-border bg-card px-3 py-1 text-xs text-muted-foreground shadow-sm">
          <span className="h-1.5 w-1.5 rounded-full bg-success" />
          Agentic RAG · multi-tenant · citation-grounded
        </span>

        <h1 className="animate-fade-up mt-6 max-w-3xl text-balance text-4xl font-semibold tracking-[-0.025em] sm:text-6xl" style={{ animationDelay: "80ms" }}>
          Ask your company's knowledge base.
          <span className="text-gradient block">Get answers you can verify.</span>
        </h1>

        <p className="animate-fade-up mt-6 max-w-2xl text-balance text-base text-muted-foreground sm:text-lg" style={{ animationDelay: "160ms" }}>
          EKBA turns HR, Finance, Legal, Engineering and Ops documentation into a single
          department-scoped assistant that answers in any language — grounded in retrieved
          evidence, with citations, or an honest refusal when the evidence isn't there.
        </p>

        <div className="animate-fade-up mt-9 flex flex-col items-center gap-3 sm:flex-row" style={{ animationDelay: "240ms" }}>
          <Link
            to="/login"
            className="group inline-flex h-11 items-center gap-2 rounded bg-brand px-6 text-sm font-medium text-brand-foreground shadow-md transition-transform hover:scale-[1.02] active:scale-[0.98]"
          >
            Open the workbench
            <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
          </Link>
          <a
            href="#architecture"
            className="inline-flex h-11 items-center rounded border border-border bg-card px-6 text-sm font-medium transition-colors hover:bg-accent"
          >
            See the architecture
          </a>
        </div>

        <div className="animate-fade-up glass-panel mt-16 grid w-full max-w-4xl grid-cols-1 gap-px overflow-hidden rounded-lg sm:grid-cols-3" style={{ animationDelay: "320ms" }}>
          <Stat icon={<ShieldCheck className="h-4 w-4 text-brand" />} label="Retrieval-time authorization" value="Never filtered from the UI" />
          <Stat icon={<Globe2 className="h-4 w-4 text-brand" />} label="Languages" value="Ask and answer in any" />
          <Stat icon={<FileCheck2 className="h-4 w-4 text-brand" />} label="Every answer" value="Cited or explicitly refused" />
        </div>
      </div>
    </section>
  );
}

function Stat({ icon, label, value }: { icon: React.ReactNode; label: string; value: string }) {
  return (
    <div className="flex flex-col items-start gap-2 bg-card/40 p-6 text-left">
      <span className="flex h-8 w-8 items-center justify-center rounded bg-accent">{icon}</span>
      <span className="text-sm font-medium">{value}</span>
      <span className="text-xs text-muted-foreground">{label}</span>
    </div>
  );
}
