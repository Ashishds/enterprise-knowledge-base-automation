import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";
import { ArrowRight, ShieldCheck } from "lucide-react";
import { useAppStore } from "@/store/useAppStore";
import type { Department } from "@/types";

const DEPARTMENTS: Department[] = ["General", "HR", "Finance", "Legal", "Engineering", "Operations"];

export function Login() {
  const signIn = useAppStore((s) => s.signIn);
  const navigate = useNavigate();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [department, setDepartment] = useState<Department>("General");

  const submit = (e: FormEvent) => {
    e.preventDefault();
    signIn({ name: name || "Demo User", email: email || "demo@example.com", department });
    navigate("/workbench");
  };

  const continueAsGuest = () => {
    signIn({ name: "Guest User", email: "guest@example.com", department: "General" });
    navigate("/workbench");
  };

  return (
    <div className="brand-glow flex min-h-dvh items-center justify-center px-6">
      <div className="glass-panel w-full max-w-sm rounded-xl p-8">
        <div className="flex flex-col items-center text-center">
          <span className="flex h-11 w-11 items-center justify-center rounded bg-brand text-brand-foreground">
            <ShieldCheck className="h-5 w-5" />
          </span>
          <h1 className="mt-4 text-lg font-semibold">EKBA Workbench</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Sign-in is optional. Click below to continue directly as guest or customize your session.
          </p>
        </div>

        <div className="mt-6 space-y-3">
          <button
            type="button"
            onClick={continueAsGuest}
            className="group flex w-full items-center justify-center gap-2 rounded bg-brand px-4 py-2.5 text-sm font-medium text-brand-foreground shadow-md transition-transform hover:scale-[1.01] active:scale-[0.99]"
          >
            Continue as Guest (Skip Sign-in)
            <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
          </button>
        </div>

        <div className="relative my-6 text-center text-xs text-muted-foreground">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-border" />
          </div>
          <span className="relative bg-card px-2 text-muted-foreground">Or customize department profile</span>
        </div>

        <form onSubmit={submit} className="space-y-4 text-left">
          <div>
            <label htmlFor="name" className="text-xs font-medium text-muted-foreground">
              Name
            </label>
            <input
              id="name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Jordan Lee (Optional)"
              className="mt-1 w-full rounded border border-input bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand"
            />
          </div>

          <div>
            <label htmlFor="email" className="text-xs font-medium text-muted-foreground">
              Work email
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="jordan@company.com (Optional)"
              className="mt-1 w-full rounded border border-input bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand"
            />
          </div>

          <div>
            <label htmlFor="department" className="text-xs font-medium text-muted-foreground">
              Department
            </label>
            <select
              id="department"
              value={department}
              onChange={(e) => setDepartment(e.target.value as Department)}
              className="mt-1 w-full rounded border border-input bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand"
            >
              {DEPARTMENTS.map((d) => (
                <option key={d} value={d}>
                  {d}
                </option>
              ))}
            </select>
            <p className="mt-1 text-[11px] text-muted-foreground">
              Retrieval is scoped to this department for the session.
            </p>
          </div>

          <button
            type="submit"
            className="flex w-full items-center justify-center gap-2 rounded border border-input bg-secondary/50 px-4 py-2 text-sm font-medium hover:bg-secondary"
          >
            Enter with custom profile
          </button>
        </form>
      </div>
    </div>
  );
}
