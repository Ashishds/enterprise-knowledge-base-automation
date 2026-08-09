"""
Tenancy Chokepoint Filter Builder.

Hard Rule (CLAUDE.md §3 Rule 6):
"NEVER let a Qdrant query run without a tenant_id filter. There is no such thing as a
legitimate cross-tenant search in this system."

This module is the SINGLE CHOKEPOINT for constructing vector store filter payloads.
It requires a valid Principal object and raises TenancyViolationError if tenant_id is absent.
"""

from __future__ import annotations

from typing import Any

from ..auth.principal import Principal


class TenancyViolationError(RuntimeError):
    """Raised when a search/filter construction is attempted without valid tenant context."""

    pass


def build_tenant_qdrant_filter(
    principal: Principal,
    *,
    department: str | None = None,
    extra_must_conditions: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Construct a mandatory Qdrant payload filter derived strictly from the verified Principal.

    Raises:
        TenancyViolationError: If principal or principal.tenant_id is missing or empty.
    """
    if not principal or not principal.tenant_id or not principal.tenant_id.strip():
        raise TenancyViolationError(
            "CRITICAL SECURITY VIOLATION: Attempted to build a Qdrant filter without a valid tenant_id"
        )

    must_conditions: list[dict[str, Any]] = [
        {"key": "tenant_id", "match": {"value": principal.tenant_id}},
        {"key": "status", "match": {"value": "active"}},
    ]

    target_dept = department or "General"
    if not principal.has_department_access(target_dept):
        raise TenancyViolationError(
            f"Principal '{principal.user_id}' in tenant '{principal.tenant_id}' is not authorized "
            f"for department '{target_dept}'"
        )

    must_conditions.append({"key": "department", "match": {"value": target_dept}})

    if extra_must_conditions:
        must_conditions.extend(extra_must_conditions)

    return {"must": must_conditions}
