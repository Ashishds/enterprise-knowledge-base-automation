import pytest

from app.agent.graph import AgentExecutionEngine
from app.agent.state import AgentState
from app.agent.tools import safe_eval_expr
from app.auth.principal import Principal
from app.rag.constants import INSUFFICIENT_EVIDENCE


@pytest.mark.agent
def test_safe_calculator_evaluates_math_without_eval():
    assert safe_eval_expr("2 + 2") == 4.0
    assert safe_eval_expr("10 * (5 - 2)") == 30.0
    assert safe_eval_expr("100 / 4") == 25.0

    with pytest.raises(ValueError, match="Unsupported"):
        safe_eval_expr("import os; os.system('dir')")


@pytest.mark.asyncio
@pytest.mark.agent
async def test_agent_graph_refuses_when_no_documents_indexed():
    principal = Principal(
        user_id="u1",
        tenant_id="t1",
        role="user",
        departments={"General"},
        correlation_id="c1",
    )
    state = AgentState(
        question="What is the remote work policy?",
        principal=principal,
    )

    engine = AgentExecutionEngine()
    res = await engine.run(state)

    assert res.terminal_reason == "refused_insufficient_evidence"
    assert res.final_answer == INSUFFICIENT_EVIDENCE
    assert res.citations == []
