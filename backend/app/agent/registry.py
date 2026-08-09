"""
Central Tool Registry.

Hard Rule (CLAUDE.md §6 & SECURITY.md §5.4a):
  - Every tool is READ-ONLY (read_only=True). There is no write, delete or configuration-mutation tool.
  - Principal is injected server-side. Model-supplied tenant_id/department/role fields are forbidden.
  - Tool arguments schemas enforce strict validation with extra="forbid".
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from ..auth.principal import Role


def _default_roles() -> frozenset[Role]:
    return frozenset(["user", "admin"])


class ToolSpec(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str
    description: str
    args_schema: type[BaseModel]
    returns_schema: type[BaseModel]
    allowed_roles: frozenset[Role] = Field(default_factory=_default_roles)
    cost_class: Literal["cheap", "moderate", "expensive"] = "cheap"
    max_calls_per_request: int = 4
    read_only: Literal[True] = True


class ToolRegistry:
    """Singleton registry of dispatchable agent tools."""

    def __init__(self) -> None:
        self._tools: dict[str, tuple[ToolSpec, Callable[..., Any]]] = {}

    def register(self, spec: ToolSpec, func: Callable[..., Any]) -> None:
        # Programmatic assertion: read_only must be True
        if not spec.read_only:
            raise ValueError(f"CRITICAL SECURITY VIOLATION: Tool '{spec.name}' is not read-only")

        # Programmatic assertion: principal fields must not be present in model args schema
        forbidden_fields = {"tenant_id", "department", "role", "owner_id", "user_id"}
        schema_fields = set(spec.args_schema.model_fields.keys())
        overlap = schema_fields.intersection(forbidden_fields)
        if overlap:
            raise ValueError(
                f"SECURITY VIOLATION: Tool '{spec.name}' args_schema contains forbidden model-supplied "
                f"principal fields: {overlap}"
            )

        self._tools[spec.name] = (spec, func)

    def get_tool_spec(self, name: str) -> ToolSpec | None:
        item = self._tools.get(name)
        return item[0] if item else None

    def list_tools_for_role(self, role: Role) -> list[ToolSpec]:
        return [spec for spec, _ in self._tools.values() if role in spec.allowed_roles]

    def has_tool(self, name: str) -> bool:
        return name in self._tools


_global_registry = ToolRegistry()


def get_tool_registry() -> ToolRegistry:
    return _global_registry
