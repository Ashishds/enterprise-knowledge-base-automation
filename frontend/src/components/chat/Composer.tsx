import { useRef, useState } from "react";
import { Paperclip, SendHorizontal, Loader2, CheckCircle2, XCircle } from "lucide-react";
import { api, ApiError } from "@/lib/api";
import { useAppStore } from "@/store/useAppStore";

export function Composer({ onSend, disabled }: { onSend: (text: string) => void; disabled: boolean }) {
  const session = useAppStore((s) => s.session);
  const [value, setValue] = useState("");
  const [uploading, setUploading] = useState(false);
  const [uploadMsg, setUploadMsg] = useState<{ text: string; success: boolean } | null>(null);
  const ref = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const submit = () => {
    const trimmed = value.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setValue("");
    requestAnimationFrame(() => ref.current?.focus());
  };

  const handleFileUpload = async (file: File | undefined) => {
    if (!file || !session) return;
    setUploading(true);
    setUploadMsg(null);
    try {
      const { document } = await api.uploadDocument(file, session.department);
      setUploadMsg({ text: `Indexed ${document.chunk_count} chunks from ${document.filename}`, success: true });
    } catch (err) {
      setUploadMsg({
        text: err instanceof ApiError ? err.message : "Upload failed",
        success: false,
      });
    } finally {
      setUploading(false);
      setTimeout(() => setUploadMsg(null), 5000);
    }
  };

  return (
    <div className="border-t border-border bg-card p-3 pb-[max(0.75rem,env(safe-area-inset-bottom))] sm:p-4">
      {uploadMsg && (
        <div
          className={`mb-2 flex items-center gap-1.5 rounded px-3 py-1.5 text-xs font-medium ${
            uploadMsg.success ? "bg-success/10 text-success" : "bg-danger/10 text-danger"
          }`}
        >
          {uploadMsg.success ? <CheckCircle2 className="h-3.5 w-3.5" /> : <XCircle className="h-3.5 w-3.5" />}
          {uploadMsg.text}
        </div>
      )}

      <div className="flex items-end gap-2 rounded-lg border border-input bg-background px-3 py-2 shadow-sm focus-within:ring-2 focus-within:ring-brand">
        <input
          ref={fileInputRef}
          type="file"
          accept=".txt,.md,.csv,.pdf,.docx"
          className="hidden"
          onChange={(e) => void handleFileUpload(e.target.files?.[0])}
        />

        <button
          type="button"
          onClick={() => fileInputRef.current?.click()}
          disabled={disabled || uploading}
          title="Upload document (.pdf, .docx, .txt, .csv, .md)"
          className="flex h-9 w-9 shrink-0 items-center justify-center rounded text-muted-foreground transition-colors hover:bg-accent hover:text-foreground disabled:opacity-40"
        >
          {uploading ? <Loader2 className="h-4 w-4 animate-spin text-brand" /> : <Paperclip className="h-4 w-4" />}
        </button>

        <textarea
          ref={ref}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              submit();
            }
          }}
          rows={1}
          placeholder="Ask about a policy, SOP, or record in your department…"
          aria-label="Message"
          className="max-h-40 flex-1 resize-none bg-transparent text-sm placeholder:text-muted-foreground focus:outline-none"
        />

        <button
          type="button"
          onClick={submit}
          disabled={disabled || !value.trim()}
          aria-label="Send message"
          className="flex h-9 w-9 shrink-0 items-center justify-center rounded bg-brand text-brand-foreground transition-transform enabled:hover:scale-105 disabled:opacity-40"
        >
          <SendHorizontal className="h-4 w-4" />
        </button>
      </div>
      <p className="mt-1.5 text-center text-[11px] text-muted-foreground">
        Answers are grounded in documents scoped to your department, with citations or an explicit refusal.
      </p>
    </div>
  );
}
