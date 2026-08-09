import pytest
from pydantic import BaseModel

from app.agent.registry import ToolRegistry, ToolSpec


class DummyArgs(BaseModel):
    query: str


class ForbiddenArgs(BaseModel):
    query: str
    tenant_id: str  # Model-supplied principal field!


class DummyReturns(BaseModel):
    result: str


@pytest.mark.agent
def test_tool_registry_rejects_model_supplied_principal_args():
    registry = ToolRegistry()
    spec = ToolSpec(
        name="test_tool",
        description="A test tool",
        args_schema=ForbiddenArgs,
        returns_schema=DummyReturns,
    )
    with pytest.raises(ValueError, match="forbidden model-supplied principal fields"):
        registry.register(spec, lambda x: x)


@pytest.mark.agent
def test_tool_registry_registers_valid_read_only_tool():
    registry = ToolRegistry()
    spec = ToolSpec(
        name="semantic_search",
        description="Search chunks",
        args_schema=DummyArgs,
        returns_schema=DummyReturns,
        read_only=True,
    )
    registry.register(spec, lambda x: x)
    assert registry.has_tool("semantic_search")
    assert registry.get_tool_spec("semantic_search") == spec
