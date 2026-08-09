import { useMemo, useState } from "react";
import DOMPurify from "dompurify";
import { marked } from "marked";
import { Bot, User } from "lucide-react";
import { cn } from "@/lib/utils";
import type { Citation, DisplayMessage } from "@/types";
import { CitationChip } from "@/components/chat/CitationChip";
import { RefusalCard } from "@/components/chat/RefusalCard";
import { ResponseMetaRow } from "@/components/chat/ResponseMetaRow";

/** Answers are untrusted content (model output, indirectly document-derived).
 * Render through marked -> DOMPurify with a strict allow-list; never
 * dangerouslySetInnerHTML on raw text (frontend.md §2, §9). */
function renderMarkdown(text: string): string {
  const html = marked.parse(text, { async: false, breaks: true }) as string;
  return DOMPurify.sanitize(html, {
    ALLOWED_TAGS: ["p", "strong", "em", "ul", "ol", "li", "code", "pre", "br", "a", "blockquote", "h3", "h4"],
    ALLOWED_ATTR: ["href"],
  });
}

export function MessageBubble({
  message,
  onRephrase,
  onSelectCitation,
}: {
  message: DisplayMessage;
  onRephrase: (text: string) => void;
  onSelectCitation: (c: Citation) => void;
}) {
  const isUser = message.role === "user";
  const html = useMemo(() => (isUser ? null : renderMarkdown(message.content)), [message.content, isUser]);
  const [rephraseDraft] = useState(message.content);

  return (
    <div className={cn("flex gap-3", isUser && "flex-row-reverse")}>
      <span
        className={cn(
          "mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-full",
          isUser ? "bg-brand text-brand-foreground" : "bg-accent text-brand"
        )}
        aria-hidden
      >
        {isUser ? <User className="h-3.5 w-3.5" /> : <Bot className="h-3.5 w-3.5" />}
      </span>

      <div className={cn("min-w-0 max-w-[42rem] flex-1", isUser && "flex flex-col items-end")}>
        {message.refusal ? (
          <RefusalCard message={message.content} onRephrase={() => onRephrase(rephraseDraft)} />
        ) : isUser ? (
          <div className="rounded-lg bg-brand px-4 py-2.5 text-sm text-brand-foreground shadow-sm">
            {message.content}
          </div>
        ) : (
          <div className="rounded-lg border border-border bg-card px-4 py-3 text-sm leading-relaxed shadow-sm">
            <div
              className="prose-sm max-w-none [&_a]:text-brand [&_a]:underline [&_code]:mono-tag [&_code]:rounded-xs [&_code]:bg-secondary [&_code]:px-1 [&_p:not(:last-child)]:mb-2"
              dangerouslySetInnerHTML={{ __html: html ?? "" }}
            />

            {message.citations && message.citations.length > 0 && (
              <div className="mt-3 flex flex-wrap gap-1.5 border-t border-border pt-3">
                {message.citations.map((c) => (
                  <CitationChip key={c.chunk_id} citation={c} onSelect={onSelectCitation} />
                ))}
              </div>
            )}

            {message.meta && <ResponseMetaRow meta={message.meta} />}
          </div>
        )}
      </div>
    </div>
  );
}
