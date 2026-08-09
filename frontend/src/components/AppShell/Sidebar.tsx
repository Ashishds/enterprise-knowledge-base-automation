import { BarChart3, FileText, MessageSquare, Settings, ShieldCheck, Users, X } from "lucide-react";
import { cn } from "@/lib/utils";
import type { WorkbenchView } from "@/pages/Workbench";

const NAV_GROUPS: { label: string; items: { icon: typeof MessageSquare; label: string; view: WorkbenchView }[] }[] = [
  { label: "Ask", items: [{ icon: MessageSquare, label: "Chat", view: "chat" }] },
  { label: "Knowledge", items: [{ icon: FileText, label: "Documents", view: "documents" }] },
  { label: "Insight", items: [{ icon: BarChart3, label: "Usage & cost", view: "usage" }] },
  {
    label: "Admin",
    items: [
      { icon: Users, label: "Users & grants", view: "users" },
      { icon: Settings, label: "Settings", view: "settings" },
    ],
  },
];

export function Sidebar({
  open,
  onClose,
  view,
  onSelectView,
}: {
  open: boolean;
  onClose: () => void;
  view: WorkbenchView;
  onSelectView: (v: WorkbenchView) => void;
}) {
  return (
    <>
      {open && (
        <div
          className="fixed inset-0 z-40 bg-foreground/20 backdrop-blur-sm lg:hidden"
          onClick={onClose}
          aria-hidden
        />
      )}
      <aside
        className={cn(
          "fixed inset-y-0 left-0 z-50 flex w-64 flex-col border-r border-border bg-card transition-transform lg:sticky lg:top-14 lg:z-0 lg:h-[calc(100dvh-3.5rem)] lg:translate-x-0",
          open ? "translate-x-0" : "-translate-x-full"
        )}
      >
        <div className="flex h-14 items-center justify-between border-b border-border px-4 lg:hidden">
          <span className="text-sm font-semibold">Navigation</span>
          <button onClick={onClose} className="rounded p-1 hover:bg-accent" aria-label="Close navigation">
            <X className="h-4 w-4" />
          </button>
        </div>

        <nav className="scrollbar-thin flex-1 space-y-6 overflow-y-auto px-3 py-4">
          {NAV_GROUPS.map((group) => (
            <div key={group.label}>
              <p className="mono-tag px-3 text-[11px] font-medium uppercase tracking-wide text-muted-foreground">
                {group.label}
              </p>
              <div className="mt-1 space-y-0.5">
                {group.items.map((item) => {
                  const active = item.view === view;
                  return (
                    <button
                      key={item.label}
                      type="button"
                      onClick={() => {
                        onSelectView(item.view);
                        onClose();
                      }}
                      className={cn(
                        "flex w-full items-center gap-2.5 rounded px-3 py-2 text-sm transition-colors",
                        active
                          ? "border-l-2 border-brand bg-accent font-medium text-accent-foreground"
                          : "border-l-2 border-transparent text-muted-foreground hover:bg-accent hover:text-accent-foreground"
                      )}
                    >
                      <item.icon className="h-4 w-4" />
                      {item.label}
                    </button>
                  );
                })}
              </div>
            </div>
          ))}
        </nav>

        <div className="border-t border-border p-3">
          <div className="flex items-center gap-2 rounded bg-secondary px-3 py-2 text-xs text-muted-foreground">
            <ShieldCheck className="h-3.5 w-3.5 text-success" />
            Retrieval scoped to your department
          </div>
        </div>
      </aside>
    </>
  );
}
