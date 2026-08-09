// Mirrors backend/app/schemas.py — kept in sync manually (frontend.md §4 flags
// this pairing as drift-prone; a generated OpenAPI client is the Phase 2 fix).

export type Department = "General" | "HR" | "Finance" | "Legal" | "Engineering" | "Operations";

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface Citation {
  chunk_id: string;
  document_id: string;
  document_name: string;
  department: string;
  snippet: string;
  similarity: number;
}

export interface ChatResponse {
  answer: string;
  citations: Citation[];
  refusal: boolean;
  clarification_needed: boolean;
  model_used: string;
  input_tokens: number;
  output_tokens: number;
  estimated_cost_usd: number;
  latency_ms: number;
  cache_hit: boolean;
  trace_id: string;
  confidence: number;
}

export interface DocumentSummary {
  id: string;
  filename: string;
  department: string;
  chunk_count: number;
  char_count: number;
  created_at: string;
}

export interface HealthResponse {
  status: string;
  environment: string;
  euri_key_configured: boolean;
  documents_indexed: number;
  chunks_indexed: number;
}

export interface DisplayMessage extends ChatMessage {
  id: string;
  citations?: Citation[];
  refusal?: boolean;
  meta?: {
    model_used: string;
    input_tokens: number;
    output_tokens: number;
    estimated_cost_usd: number;
    latency_ms: number;
    cache_hit: boolean;
    trace_id: string;
    confidence: number;
  };
}
