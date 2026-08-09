import { LogOut, Menu, ShieldCheck } from "lucide-react";
import { ThemeToggle } from "@/components/ThemeToggle";
import { useAppStore } from "@/store/useAppStore";
import { useNavigate } from "react-router-dom";

export function Header({ onMenuClick }: { onMenuClick: () => void }) {
  const session = useAppStore((s) => s.session);
  const signOut = useAppStore((s) => s.signOut);
  const navigate = useNavigate();

  return (
    <header className="sticky top-0 z-40 flex h-14 items-center justify-between border-b border-border bg-card px-4">
      <div className="flex items-center gap-3">
        <button
          type="button"
          onClick={onMenuClick}
          className="inline-flex h-9 w-9 items-center justify-center rounded text-muted-foreground hover:bg-accent lg:hidden"
          aria-label="Toggle navigation"
        >
          <Menu className="h-4 w-4" />
        </button>
        <span className="flex items-center gap-2 font-semibold tracking-tight">
          <span className="flex h-7 w-7 items-center justify-center rounded bg-brand text-brand-foreground">
            <ShieldCheck className="h-3.5 w-3.5" />
          </span>
          EKBA
        </span>
        {session && (
          <span className="mono-tag hidden rounded-full border border-border bg-secondary px-2 py-0.5 text-xs text-muted-foreground sm:inline">
            {session.department}
          </span>
        )}
      </div>

      <div className="flex items-center gap-2">
        <ThemeToggle />
        {session && (
          <>
            <span className="hidden text-sm text-muted-foreground sm:inline">{session.name}</span>
            <button
              type="button"
              onClick={() => {
                signOut();
                navigate("/");
              }}
              aria-label="Sign out"
              className="inline-flex h-9 w-9 items-center justify-center rounded text-muted-foreground hover:bg-accent hover:text-destructive"
            >
              <LogOut className="h-4 w-4" />
            </button>
          </>
        )}
      </div>
    </header>
  );
}
