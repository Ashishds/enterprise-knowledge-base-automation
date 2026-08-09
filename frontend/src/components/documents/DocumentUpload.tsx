import { useRef, useState } from "react";
import { CheckCircle2, Loader2, UploadCloud, XCircle } from "lucide-react";
import { api, ApiError } from "@/lib/api";
import { useAppStore } from "@/store/useAppStore";

type Status = "idle" | "running" | "completed" | "failed";

export function DocumentUpload({ onUploaded }: { onUploaded: () => void }) {
  const session = useAppStore((s) => s.session);
  const [status, setStatus] = useState<Status>("idle");
  const [message, setMessage] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFile = async (file: File | undefined) => {
    if (!file || !session) return;
    setStatus("running");
    setMessage(null);
    try {
      const { document } = await api.uploadDocument(file, session.department);
      setStatus("completed");
      setMessage(`Indexed ${document.chunk_count} chunks from ${document.filename}.`);
      onUploaded();
    } catch (err) {
      setStatus("failed");
      const errDetail = err instanceof ApiError ? err.message : (err instanceof Error ? err.message : "Upload failed.");
      setMessage(errDetail.includes("fetch") ? "Could not connect to backend server. Is FastAPI server running on port 8000?" : errDetail);
    }

  };

  return (
    <div
      className="rounded-lg border border-dashed border-border bg-secondary/30 p-5 text-center transition-colors hover:border-brand"
      onDragOver={(e) => e.preventDefault()}
      onDrop={(e) => {
        e.preventDefault();
        void handleFile(e.dataTransfer.files?.[0]);
      }}
    >
      <input
        ref={inputRef}
        type="file"
        accept=".txt,.md,.csv,.pdf,.docx"
        className="hidden"
        onChange={(e) => void handleFile(e.target.files?.[0])}
      />
      <button
        type="button"
        onClick={() => inputRef.current?.click()}
        className="flex w-full flex-col items-center gap-2 text-sm"
      >
        {status === "running" ? (
          <Loader2 className="h-6 w-6 animate-spin text-brand" />
        ) : (
          <UploadCloud className="h-6 w-6 text-muted-foreground" />
        )}
        <span className="font-medium">Drop a document or click to upload</span>
        <span className="text-xs text-muted-foreground">.txt · .md · .csv · .pdf · .docx — scoped to {session?.department}</span>
      </button>

      {message && (
        <p
          className={`mt-3 inline-flex items-center gap-1.5 text-xs ${
            status === "failed" ? "text-danger" : "text-success"
          }`}
        >
          {status === "failed" ? <XCircle className="h-3.5 w-3.5" /> : <CheckCircle2 className="h-3.5 w-3.5" />}
          {message}
        </p>
      )}
    </div>
  );
}
