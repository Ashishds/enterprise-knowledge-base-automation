import {
  BookOpenCheck,
  Building2,
  Gauge,
  Languages,
  ScanSearch,
  ShieldAlert,
} from "lucide-react";

const FEATURES = [
  {
    icon: ScanSearch,
    title: "Ingests anything",
    body: "PDF, DOCX, XLSX, PPTX, images, audio and video are all made retrievable — tables, diagrams and media included, not just plain text.",
  },
  {
    icon: Building2,
    title: "Department-scoped by design",
    body: "Authorization is enforced at retrieval time. A chunk outside your tenant and department is never returned — not hidden, never fetched.",
  },
  {
    icon: Languages,
    title: "Answers in any language",
    body: "Ask in one language, retrieve from documents in another. Every answer cites the exact document, version and page.",
  },
  {
    icon: ShieldAlert,
    title: "Defends itself",
    body: "Hardened against prompt injection — direct and embedded in uploaded documents — system-prompt extraction and cross-tenant probing.",
  },
  {
    icon: BookOpenCheck,
    title: "Refuses honestly",
    body: "When the evidence is insufficient, EKBA says so plainly with a fixed refusal message, rather than guessing.",
  },
  {
    icon: Gauge,
    title: "Cost measured, not estimated",
    body: "Every request records tokens, model, route, cache status and dollar cost — visible in the response metadata, not buried in a bill.",
  },
];

export function Features() {
  return (
    <section id="capabilities" className="container py-24">
      <div className="mx-auto max-w-2xl text-center">
        <h2 className="text-2xl font-semibold tracking-[-0.02em] sm:text-3xl">Built for the way enterprises actually work</h2>
        <p className="mt-3 text-muted-foreground">
          Not a fixed retrieve-then-generate chain — an agent that plans, retrieves, checks its own
          evidence, and knows when to stop.
        </p>
      </div>

      <div className="mt-14 grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
        {FEATURES.map(({ icon: Icon, title, body }, i) => (
          <div
            key={title}
            className="animate-fade-up group rounded-lg border border-border bg-card p-6 shadow-sm transition-shadow hover:shadow-md"
            style={{ animationDelay: `${i * 60}ms` }}
          >
            <span className="flex h-10 w-10 items-center justify-center rounded bg-accent text-brand transition-colors group-hover:bg-brand group-hover:text-brand-foreground">
              <Icon className="h-5 w-5" />
            </span>
            <h3 className="mt-4 text-base font-semibold">{title}</h3>
            <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{body}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
