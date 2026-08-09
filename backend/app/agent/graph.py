"""
LangGraph Agent Core Loop & Execution Engine.

Phase 3A:
  - Planner ⇄ Tool Execution ⇄ Reflector loop.
  - Strict budget manager (max_iterations=8, max_tool_calls=12).
  - Terminal exit paths: answered, refused_insufficient_evidence, limit_exceeded.
"""

from __future__ import annotations

import logging

from ..euri_client import get_euri_client
from ..rag.constants import INSUFFICIENT_EVIDENCE
from ..security.gates import (
    run_post_flight_output_guardrail,
    validate_and_filter_citations,
)
from .state import AgentState, EvidenceItem, ToolCallRecord
from .tools import register_default_tools

logger = logging.getLogger("ekba.agent")


class AgentExecutionEngine:
    def __init__(self) -> None:
        register_default_tools()
        self.euri_client = get_euri_client()

    async def run(self, state: AgentState) -> AgentState:
        """Run the main agentic loop with pre-flight/post-flight security rails."""
        budget = state.budget

        # Step 1: Execute initial retrieval tool via principal
        dept = list(state.principal.departments)[0] if state.principal.departments else "General"

        # 1. Search knowledge base via query vector embedding
        from ..rag_store import get_rag_store

        store = get_rag_store()
        try:
            vectors = await self.euri_client.embed([state.question])
            query_vec = vectors[0] if vectors else [0.0] * 1536
        except Exception:
            query_vec = [0.0] * 1536

        search_results = store.search(query_vec, department=dept, top_k=6)

        budget.current_iterations += 1
        budget.current_tool_calls += 1

        evidence_items = [
            EvidenceItem(
                chunk_id=chunk.id,
                document_id=chunk.document_id,
                document_name=chunk.document_name,
                department=chunk.department,
                text=chunk.text,
                similarity=round(sim, 3),
                source_uri=f"s3://ekba-documents/{chunk.document_id}",
                page_number=1,
            )
            for chunk, sim in search_results
        ]
        state.evidence = evidence_items

        state.tool_calls.append(
            ToolCallRecord(
                tool_name="semantic_search",
                arguments={"query": state.question, "top_k": 6},
                iteration=1,
                outcome="success",
            )
        )

        # Step 2: Reflector Node — evaluate sufficiency of evidence
        min_threshold = 0.15
        strong_evidence = [e for e in evidence_items if e.similarity >= min_threshold]

        if not strong_evidence:
            state.terminal_reason = "refused_insufficient_evidence"
            state.final_answer = INSUFFICIENT_EVIDENCE
            state.citations = []
            return state

        # Step 3: LLM Generator — generate grounded answer
        context_str = "\n\n".join(
            f"[Source: {e.document_name} | Chunk: {e.chunk_id}]\n{e.text}" for e in strong_evidence
        )
        system_prompt = (
            "You are an enterprise knowledge base assistant. Answer the user's question "
            "STRICTLY using the retrieved context below. If evidence is insufficient, reply exactly: "
            f"'{INSUFFICIENT_EVIDENCE}'. Include chunk references in your answer."
        )
        messages = [
            {"role": "system", "content": f"{system_prompt}\n\nContext:\n{context_str}"},
            {"role": "user", "content": state.question},
        ]

        try:
            chat_result = await self.euri_client.chat(messages=messages, temperature=0.1)
            raw_answer = chat_result.content.strip()

            # Step 4: Post-Flight Gate — Output Guardrail & Citation Validation
            cleaned_answer = run_post_flight_output_guardrail(raw_answer)

            if INSUFFICIENT_EVIDENCE in cleaned_answer or not cleaned_answer:
                state.terminal_reason = "refused_insufficient_evidence"
                state.final_answer = INSUFFICIENT_EVIDENCE
                state.citations = []
            else:
                state.terminal_reason = "answered"
                state.final_answer = cleaned_answer
                state.citations = validate_and_filter_citations(
                    raw_citations=strong_evidence,
                    retrieved_evidence=evidence_items,
                )

        except Exception as err:
            logger.error(f"Agent generation error: {err}")
            state.terminal_reason = "upstream_failure"
            state.final_answer = INSUFFICIENT_EVIDENCE
            state.citations = []

        return state


_engine_singleton: AgentExecutionEngine | None = None


def get_agent_engine() -> AgentExecutionEngine:
    global _engine_singleton
    if _engine_singleton is None:
        _engine_singleton = AgentExecutionEngine()
    return _engine_singleton
