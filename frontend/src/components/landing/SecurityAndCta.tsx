import { Link } from "react-router-dom";
import { KeyRound, Lock, ScrollText } from "lucide-react";

const CONTROLS = [
  {
    icon: Lock,
    title: "Authorization at retrieval time",
    body: "Never filtered from the UI afterward. A chunk your tenant and department don't grant is never returned from the vector store.",
  },
  {
    icon: ScrollText,
    title: "Read-only tools, always",
    body: "Every agent tool is read-only and role-filtered. Shell access, arbitrary HTTP, raw SQL and anything that writes or deletes are absent — forever.",
  },
  {
    icon: KeyRound,
    title: "Secrets stay server-side",
    body: "API keys live in a secrets manager, injected at runtime. Never in frontend code, never in a log, never in the client bundle.",
  },
];

export function SecurityAndCta() {
  return (
    <>
      <section id="security" className="container py-24">
        <div className="grid grid-cols-1 gap-10 lg:grid-cols-[1fr_1.2fr] lg:items-center">
          <div>
            <h2 className="text-2xl font-semibold tracking-[-0.02em] sm:text-3xl">
              Security is the architecture, not a checklist
            </h2>
            <p className="mt-3 max-w-md text-muted-foreground">
              An agent that could decide to skip authorization or citation validation would be a
              vulnerability, not a feature.
            </p>
          </div>
          <div className="space-y-4">
            {CONTROLS.map(({ icon: Icon, title, body }) => (
              <div key={title} className="flex gap-4 rounded-lg border border-border bg-card p-5 shadow-sm">
                <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded bg-accent text-brand">
                  <Icon className="h-4 w-4" />
                </span>
                <div>
                  <h3 className="text-sm font-semibold">{title}</h3>
                  <p className="mt-1 text-sm text-muted-foreground">{body}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="container pb-24">
        <div className="glass-panel brand-glow relative overflow-hidden rounded-xl px-8 py-16 text-center">
          <h2 className="mx-auto max-w-xl text-2xl font-semibold tracking-[-0.02em] sm:text-3xl">
            Point it at your documents. Ask it anything.
          </h2>
          <p className="mx-auto mt-3 max-w-md text-muted-foreground">
            Sign in, upload a document, and try a cited, department-scoped answer in under a minute.
          </p>
          <Link
            to="/login"
            className="mt-8 inline-flex h-11 items-center rounded bg-brand px-6 text-sm font-medium text-brand-foreground shadow-md transition-transform hover:scale-[1.02] active:scale-[0.98]"
          >
            Open the workbench
          </Link>
        </div>
      </section>
    </>
  );
}
