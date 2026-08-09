"""
Read-Only Tool Implementations for LangGraph Agent.

Phase 3A:
  - All tools are strictly read-only (read_only=True).
  - Principal is passed server-side; model-supplied principal arguments are forbidden.
  - Safe calculator evaluating expressions via Python AST.
"""

from __future__ import annotations

import ast
import operator as op
from typing import Any

from pydantic import BaseModel, Field

from ..auth.principal import Principal
from ..rag.constants import INSUFFICIENT_EVIDENCE
from ..rag_store import get_rag_store
from .registry import ToolSpec, get_tool_registry

# Safe operators for calculator
SAFE_OPERATORS: dict[type[ast.AST], Any] = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.USub: op.neg,
}


def safe_eval_expr(expr: str) -> float:
    """Safe mathematical expression evaluator using Python AST parsing (no eval)."""

    def _eval(node: ast.AST) -> float:
        if isinstance(node, ast.Constant) and isinstance(node.value, int | float):
            return float(node.value)
        elif isinstance(node, ast.BinOp):
            left = _eval(node.left)
            right = _eval(node.right)
            operator_fn = SAFE_OPERATORS.get(type(node.op))
            if not operator_fn:
                raise ValueError(f"Unsupported operator: {type(node.op)}")
            return float(operator_fn(left, right))
        elif isinstance(node, ast.UnaryOp):
            operand = _eval(node.operand)
            operator_fn = SAFE_OPERATORS.get(type(node.op))
            if not operator_fn:
                raise ValueError(f"Unsupported operator: {type(node.op)}")
            return float(operator_fn(operand))
        else:
            raise ValueError(f"Unsupported AST node: {type(node)}")

    try:
        parsed = ast.parse(expr.strip(), mode="eval")
        return _eval(parsed.body)
    except (SyntaxError, ValueError) as err:
        raise ValueError(f"Unsupported mathematical expression: {err}") from err


# --- 1. Semantic Search Tool ---
class SemanticSearchArgs(BaseModel):
    query: str = Field(..., description="The search query string")
    top_k: int = Field(default=4, ge=1, le=10)


class SemanticSearchReturns(BaseModel):
    chunks: list[dict[str, Any]]


def semantic_search_tool(principal: Principal, query: str, top_k: int = 4) -> dict[str, Any]:
    """Search knowledge base scoped strictly to principal's department."""
    store = get_rag_store()
    dept = list(principal.departments)[0] if principal.departments else "General"
    query_vec = [0.0] * 1536
    results = store.search(query_vec, department=dept, top_k=top_k)

    chunks_data = [
        {
            "chunk_id": chunk.id,
            "document_id": chunk.document_id,
            "document_name": chunk.document_name,
            "department": chunk.department,
            "text": chunk.text,
            "similarity": round(sim, 3),
        }
        for chunk, sim in results
    ]

    return {"chunks": chunks_data}


# --- 2. Safe Calculator Tool ---
class CalculatorArgs(BaseModel):
    expression: str = Field(..., description="Mathematical expression e.g. '120 * 1.15'")


class CalculatorReturns(BaseModel):
    result: float


def calculator_tool(expression: str) -> dict[str, Any]:
    res = safe_eval_expr(expression)
    return {"result": res}


# --- 3. Refusal Tool ---
class RefuseArgs(BaseModel):
    reason: str = Field(default="insufficient_evidence")


class RefuseReturns(BaseModel):
    refusal_string: str


def refuse_tool(reason: str = "insufficient_evidence") -> dict[str, Any]:
    return {"refusal_string": INSUFFICIENT_EVIDENCE}


def register_default_tools() -> None:
    registry = get_tool_registry()

    if not registry.has_tool("semantic_search"):
        registry.register(
            ToolSpec(
                name="semantic_search",
                description="Search department SOPs and knowledge base documents",
                args_schema=SemanticSearchArgs,
                returns_schema=SemanticSearchReturns,
                cost_class="moderate",
            ),
            semantic_search_tool,
        )

    if not registry.has_tool("calculator"):
        registry.register(
            ToolSpec(
                name="calculator",
                description="Safely evaluate mathematical expressions",
                args_schema=CalculatorArgs,
                returns_schema=CalculatorReturns,
                cost_class="cheap",
            ),
            calculator_tool,
        )

    if not registry.has_tool("refuse"):
        registry.register(
            ToolSpec(
                name="refuse",
                description="Refuse to answer when evidence is insufficient",
                args_schema=RefuseArgs,
                returns_schema=RefuseReturns,
                cost_class="cheap",
            ),
            refuse_tool,
        )
