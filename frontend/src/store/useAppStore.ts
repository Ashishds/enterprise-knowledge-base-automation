import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { Department } from "@/types";

/**
 * This is a LOCAL DEMO session store, not real auth. Production EKBA uses
 * AWS Cognito JWTs, held in memory (never localStorage) with server-derived
 * tenant/department/role — see .claude/rules/frontend.md §2. Persisting a
 * mock profile here is fine because it carries no access token and grants
 * no real permission; the backend does not trust it for anything sensitive.
 */
interface Session {
  name: string;
  email: string;
  department: Department;
}

interface AppState {
  session: Session | null;
  theme: "light" | "dark";
  signIn: (session: Session) => void;
  signOut: () => void;
  toggleTheme: () => void;
}

const initialTheme = (): "light" | "dark" =>
  typeof document !== "undefined" && document.documentElement.classList.contains("dark") ? "dark" : "light";

export const useAppStore = create<AppState>()(
  persist(
    (set, get) => ({
      session: null,
      theme: initialTheme(),
      signIn: (session) => set({ session }),
      signOut: () => set({ session: null }),
      toggleTheme: () => {
        const next = get().theme === "dark" ? "light" : "dark";
        document.documentElement.classList.toggle("dark", next === "dark");
        localStorage.setItem("ekba-theme", next);
        set({ theme: next });
      },
    }),
    { name: "ekba-demo-session", partialize: (state) => ({ session: state.session }) }
  )
);
