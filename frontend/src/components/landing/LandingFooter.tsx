export function LandingFooter() {
  return (
    <footer className="border-t border-border/60">
      <div className="container flex flex-col items-center justify-between gap-4 py-10 text-sm text-muted-foreground sm:flex-row">
        <p>© {new Date().getFullYear()} EKBA. Proprietary — internal use.</p>
        <div className="flex items-center gap-6">
          <span className="mono-tag">v0.1.0-local</span>
          <span className="rounded-full border border-border px-2 py-0.5 text-xs">local dev environment</span>
        </div>
      </div>
    </footer>
  );
}
