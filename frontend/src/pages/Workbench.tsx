import { useCallback, useEffect, useState } from "react";
import { Navigate } from "react-router-dom";
import { useAppStore } from "@/store/useAppStore";
import { api } from "@/lib/api";
import type { DocumentSummary } from "@/types";
import { Header } from "@/components/AppShell/Header";
import { Sidebar } from "@/components/AppShell/Sidebar";
import { AppFooter } from "@/components/AppShell/AppFooter";
import { ChatWindow } from "@/components/chat/ChatWindow";
import { DocumentUpload } from "@/components/documents/DocumentUpload";
import { DocumentList } from "@/components/documents/DocumentList";
import { UsageView } from "@/components/insight/UsageView";
import { UsersView } from "@/components/admin/UsersView";
import { SettingsView } from "@/components/admin/SettingsView";

export type WorkbenchView = "chat" | "documents" | "usage" | "users" | "settings";

export function Workbench() {
  const session = useAppStore((s) => s.session);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [view, setView] = useState<WorkbenchView>("chat");
  const [documents, setDocuments] = useState<DocumentSummary[]>([]);
  const [loadingDocs, setLoadingDocs] = useState(false);

  const refreshDocuments = useCallback(async () => {
    if (!session) return;
    setLoadingDocs(true);
    try {
      setDocuments(await api.listDocuments(session.department));
    } catch {
      /* surfaced via empty state; the demo API is expected to be reachable locally */
    } finally {
      setLoadingDocs(false);
    }
  }, [session]);

  useEffect(() => {
    void refreshDocuments();
  }, [refreshDocuments]);

  if (!session) return <Navigate to="/login" replace />;

  return (
    <div className="flex h-dvh flex-col">
      <Header onMenuClick={() => setSidebarOpen(true)} />
      <div className="flex min-h-0 flex-1">
        <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} view={view} onSelectView={setView} />

        {view === "chat" && <ChatWindow />}
        {view === "documents" && (
          <div className="scrollbar-thin min-h-0 flex-1 overflow-y-auto p-6">
            <div className="mx-auto max-w-2xl">
              <div className="mb-6">
                <h1 className="text-xl font-semibold tracking-[-0.02em]">Documents</h1>
                <p className="mt-1 text-sm text-muted-foreground">
                  Upload files for the <strong className="text-foreground">{session.department}</strong> department.
                  They're chunked, embedded and become searchable immediately.
                </p>
              </div>
              <DocumentUpload onUploaded={refreshDocuments} />
              <div className="mt-6">
                <DocumentList documents={documents} loading={loadingDocs} />
              </div>
            </div>
          </div>
        )}
        {view === "usage" && <UsageView />}
        {view === "users" && <UsersView />}
        {view === "settings" && <SettingsView />}
      </div>
      <AppFooter />
    </div>
  );
}
