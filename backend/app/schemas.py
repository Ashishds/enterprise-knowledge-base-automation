"""Pydantic request/response contracts. Kept in sync manually with the
frontend TypeScript types in frontend/src/types/index.ts — see .claude/rules
frontend.md §4 for why that pairing matters."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str  # "user" | "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    department: str = Field(..., description="Scopes retrieval; never trust client for real auth")
    history: list[ChatMessage] = Field(default_factory=list)


class Citation(BaseModel):
    chunk_id: str
    document_id: str
    document_name: str
    department: str
    snippet: str
    similarity: float


class ChatResponse(BaseModel):
    answer: str
    citations: list[Citation] = Field(default_factory=list)
    refusal: bool = False
    clarification_needed: bool = False
    model_used: str
    input_tokens: int
    output_tokens: int
    estimated_cost_usd: float
    latency_ms: int
    cache_hit: bool
    trace_id: str
    confidence: float


class DocumentSummary(BaseModel):
    id: str
    filename: str
    department: str
    chunk_count: int
    char_count: int
    created_at: str


class UploadResponse(BaseModel):
    document: DocumentSummary


class HealthResponse(BaseModel):
    status: str
    environment: str
    euri_key_configured: bool
    documents_indexed: int
    chunks_indexed: int
