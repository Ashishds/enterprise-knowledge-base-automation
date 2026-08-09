import type { ChatMessage, ChatResponse, DocumentSummary, HealthResponse } from "@/types";

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "";


export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      ...(init?.body && !(init.body instanceof FormData) ? { "Content-Type": "application/json" } : {}),
      ...init?.headers,
    },
  });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail ?? detail;
    } catch {
      /* body wasn't JSON */
    }
    throw new ApiError(res.status, detail);
  }
  return res.json() as Promise<T>;
}

export const api = {
  health: () => request<HealthResponse>("/api/health"),

  chat: (message: string, department: string, history: ChatMessage[]) =>
    request<ChatResponse>("/api/chat", {
      method: "POST",
      body: JSON.stringify({ message, department, history }),
    }),

  listDocuments: (department?: string) =>
    request<DocumentSummary[]>(`/api/documents${department ? `?department=${encodeURIComponent(department)}` : ""}`),

  uploadDocument: (file: File, department: string) => {
    const form = new FormData();
    form.append("file", file);
    form.append("department", department);
    return request<{ document: DocumentSummary }>("/api/documents/upload", {
      method: "POST",
      body: form,
    });
  },
};
