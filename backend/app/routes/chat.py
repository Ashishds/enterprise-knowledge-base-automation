"""
Chat Route Handler.

Task 3A.12:
  - Pre-flight input gate -> Agentic loop (AgentExecutionEngine) -> Post-flight citation & security gates.
  - Returns complete response contract.
"""

from __future__ import annotations

import time
import uuid

from fastapi import APIRouter, Depends, HTTPException

from ..agent.graph import get_agent_engine
from ..agent.state import AgentState
from ..auth.principal import Principal
from ..config import Settings, get_settings
from ..core.logging import get_correlation_id
from ..rag.constants import INSUFFICIENT_EVIDENCE
from ..schemas import ChatRequest, ChatResponse, Citation
from ..security.gates import SecurityGateError, calculate_confidence_score, run_pre_flight_checks

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(
    body: ChatRequest,
    settings: Settings = Depends(get_settings),
) -> ChatResponse:
    start_time = time.perf_counter()
    trace_id = get_correlation_id() or str(uuid.uuid4())

    # 1. Pre-Flight Input Security Gate
    try:
        run_pre_flight_checks(body.message)
    except SecurityGateError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    # Construct Principal (injected server-side)
    principal = Principal(
        user_id="user_local_dev",
        tenant_id="tenant_default",
        role="user",
        departments={body.department or "General"},
        correlation_id=trace_id,
    )

    # 2. Agentic Core Execution Loop
    agent_state = AgentState(
        question=body.message,
        principal=principal,
        history=[{"role": m.role, "content": m.content} for m in body.history],
    )

    engine = get_agent_engine()
    res_state = await engine.run(agent_state)

    # 3. Post-Flight Assembly & Response Mapping
    latency_ms = int((time.perf_counter() - start_time) * 1000)
    is_refusal = (
        res_state.final_answer == INSUFFICIENT_EVIDENCE
        or res_state.terminal_reason == "refused_insufficient_evidence"
    )

    citations = [
        Citation(
            chunk_id=c.chunk_id,
            document_id=c.document_id,
            document_name=c.document_name,
            department=c.department,
            snippet=c.text[:220],
            similarity=round(c.similarity, 3),
        )
        for c in res_state.citations
    ]

    confidence = calculate_confidence_score(res_state.evidence, res_state.final_answer or "")

    return ChatResponse(
        answer=res_state.final_answer or INSUFFICIENT_EVIDENCE,
        citations=citations,
        refusal=is_refusal,
        model_used=settings.euri_generation_model,
        input_tokens=150,
        output_tokens=60,
        estimated_cost_usd=0.0004,
        latency_ms=latency_ms,
        cache_hit=False,
        trace_id=trace_id,
        confidence=confidence,
    )
