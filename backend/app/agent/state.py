"""
LangGraph Agent State.

Typed Pydantic state model for the agentic planner/reflector/tool execution loop.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

from ..auth.principal import Principal

TerminalReason = Literal[
    "answered",
    "refused_insufficient_evidence",
    "refused_guardrail",
    "refused_out_of_scope",
    "clarification_requested",
    "limit_exceeded",
    "upstream_failure",
]


class EvidenceItem(BaseModel):
    chunk_id: str
    document_id: str
    document_name: str
    department: str
    text: str
    similarity: float
    source_uri: str
    page_number: int | None = None
    time_offset_ms: int | None = None


class ToolCallRecord(BaseModel):
    tool_name: str
    arguments: dict[str, Any]
    iteration: int
    outcome: str  # success | error
    error_detail: str | None = None


class AgentBudget(BaseModel):
    max_iterations: int = 8
    max_tool_calls: int = 12
    max_calls_per_tool: int = 4
    max_chunks: int = 40
    max_tokens: int = 60000
    max_wall_time_sec: float = 45.0

    current_iterations: int = 0
    current_tool_calls: int = 0
    tool_call_counts: dict[str, int] = Field(default_factory=dict)


class AgentState(BaseModel):
    question: str
    principal: Principal
    history: list[dict[str, str]] = Field(default_factory=list)
    evidence: list[EvidenceItem] = Field(default_factory=list)
    tool_calls: list[ToolCallRecord] = Field(default_factory=list)
    budget: AgentBudget = Field(default_factory=AgentBudget)

    plan: str | None = None
    reflector_verdict: str | None = None
    clarification_question: str | None = None
    terminal_reason: TerminalReason | None = None
    final_answer: str | None = None
    citations: list[EvidenceItem] = Field(default_factory=list)
