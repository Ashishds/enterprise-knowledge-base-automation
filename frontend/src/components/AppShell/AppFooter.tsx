export function AppFooter() {
  return (
    <footer className="flex h-10 shrink-0 items-center justify-between border-t border-border bg-card px-4 text-xs text-muted-foreground">
      <span className="mono-tag">ekba v0.1.0-local</span>
      <div className="flex items-center gap-4">
        <span className="rounded-full border border-border px-2 py-0.5">local dev</span>
        <a href="#" className="hover:text-foreground">
          Status
        </a>
        <a href="#" className="hover:text-foreground">
          Support
        </a>
      </div>
    </footer>
  );
}
