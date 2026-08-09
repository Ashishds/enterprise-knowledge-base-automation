import { Link } from "react-router-dom";
import { ShieldCheck } from "lucide-react";
import { ThemeToggle } from "@/components/ThemeToggle";

export function LandingNav() {
  return (
    <header className="sticky top-0 z-50 border-b border-border/60 bg-background/70 backdrop-blur-lg">
      <div className="container flex h-16 items-center justify-between">
        <Link to="/" className="flex items-center gap-2 font-semibold tracking-tight">
          <span className="flex h-8 w-8 items-center justify-center rounded bg-brand text-brand-foreground">
            <ShieldCheck className="h-4 w-4" />
          </span>
          <span>
            EKBA<span className="text-muted-foreground font-normal"> · Enterprise Knowledge Base</span>
          </span>
        </Link>

        <nav className="hidden items-center gap-8 text-sm text-muted-foreground md:flex">
          <a href="#capabilities" className="transition-colors hover:text-foreground">
            Capabilities
          </a>
          <a href="#architecture" className="transition-colors hover:text-foreground">
            Architecture
          </a>
          <a href="#security" className="transition-colors hover:text-foreground">
            Security
          </a>
        </nav>

        <div className="flex items-center gap-3">
          <ThemeToggle />
          <Link
            to="/login"
            className="inline-flex h-9 items-center rounded bg-brand px-4 text-sm font-medium text-brand-foreground shadow-sm transition-transform hover:scale-[1.02] active:scale-[0.98]"
          >
            Sign in
          </Link>
        </div>
      </div>
    </header>
  );
}
