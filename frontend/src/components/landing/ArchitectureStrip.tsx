const PIPELINE = [
  "Pre-flight: auth, validation, injection scan, cache lookup",
  "Planner decides what to retrieve and how",
  "Tool router calls read-only, role-filtered tools",
  "Reflector checks whether evidence is sufficient",
  "Citation validation + output guardrail",
  "Grounded answer, or an honest refusal",
];

const STACK = [
  "React + TypeScript",
  "FastAPI",
  "LangGraph",
  "Qdrant",
  "Supabase",
  "AWS Cognito",
  "AWS S3",
  "AWS EKS",
  "Euri AI Gateway",
];

export function ArchitectureStrip() {
  return (
    <section id="architecture" className="border-y border-border/60 bg-secondary/40">
      <div className="container py-24">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="text-2xl font-semibold tracking-[-0.02em] sm:text-3xl">
            Deterministic gates around an agentic core
          </h2>
          <p className="mt-3 text-muted-foreground">
            The model plans; it never decides what it's permitted to do. Authorization, citation
            validation and refusal are enforced in code, not requested in a prompt.
          </p>
        </div>

        <div className="glass-panel mx-auto mt-12 max-w-3xl rounded-lg p-6 sm:p-8">
          <ol className="space-y-0">
            {PIPELINE.map((step, i) => (
              <li key={step} className="relative flex gap-4 pb-8 last:pb-0">
                {i < PIPELINE.length - 1 && (
                  <span aria-hidden className="absolute left-[15px] top-8 h-full w-px bg-border" />
                )}
                <span className="mono-tag flex h-8 w-8 shrink-0 items-center justify-center rounded-full border border-border bg-card text-xs font-medium text-brand">
                  {i + 1}
                </span>
                <span className="pt-1 text-sm text-foreground/90">{step}</span>
              </li>
            ))}
          </ol>
        </div>

        <div className="mx-auto mt-14 flex max-w-3xl flex-wrap items-center justify-center gap-2">
          {STACK.map((item) => (
            <span
              key={item}
              className="mono-tag rounded-full border border-border bg-card px-3 py-1 text-xs text-muted-foreground shadow-sm"
            >
              {item}
            </span>
          ))}
        </div>
      </div>
    </section>
  );
}
