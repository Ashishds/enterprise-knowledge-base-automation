import { ShieldCheck, UserCheck, Key, Lock } from "lucide-react";
import { useAppStore } from "@/store/useAppStore";

export function UsersView() {
  const session = useAppStore((s) => s.session);

  const users = [
    { name: session?.name || "Guest User", email: session?.email || "guest@example.com", role: "Department Lead", dept: session?.department || "General", status: "Active" },
    { name: "Ashish S.", email: "ashish@company.com", role: "System Admin", dept: "Engineering", status: "Active" },
    { name: "Sarah M.", email: "sarah@company.com", role: "Policy Manager", dept: "HR", status: "Active" },
  ];

  return (
    <div className="scrollbar-thin min-h-0 flex-1 overflow-y-auto p-6">
      <div className="mx-auto max-w-4xl space-y-6">
        <div>
          <h1 className="text-xl font-semibold tracking-[-0.02em]">Users & Access Grants</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Role-Based Access Control (RBAC) and department tenant isolation policies.
          </p>
        </div>

        <div className="glass-panel rounded-lg p-5">
          <div className="flex items-center gap-2 mb-4">
            <ShieldCheck className="h-5 w-5 text-brand" />
            <h3 className="text-sm font-medium">Tenant Isolation Guardrail</h3>
          </div>
          <p className="text-xs text-muted-foreground leading-relaxed">
            All vector similarity searches on Qdrant are automatically enforced with a mandatory <code className="bg-secondary px-1.5 py-0.5 rounded text-foreground font-mono">tenant_id</code> payload filter matching the logged-in user's department ({session?.department}).
          </p>
        </div>

        <div className="glass-panel rounded-lg overflow-hidden">
          <div className="px-5 py-4 border-b border-border flex items-center justify-between">
            <h3 className="text-sm font-medium">Department Members</h3>
            <span className="text-xs bg-brand/10 text-brand px-2.5 py-1 rounded font-medium">3 Active Accounts</span>
          </div>
          <div className="divide-y divide-border">
            {users.map((u, i) => (
              <div key={i} className="px-5 py-3.5 flex items-center justify-between text-sm">
                <div>
                  <p className="font-medium">{u.name}</p>
                  <p className="text-xs text-muted-foreground">{u.email}</p>
                </div>
                <div className="flex items-center gap-4 text-xs">
                  <span className="bg-secondary px-2.5 py-1 rounded">{u.dept}</span>
                  <span className="text-muted-foreground">{u.role}</span>
                  <span className="flex items-center gap-1 text-success font-medium">
                    <UserCheck className="h-3.5 w-3.5" />
                    {u.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
