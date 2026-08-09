"""
Principal Model.

The authenticated identity constructed server-side from a verified Cognito JWT
and server-side grant lookup. Handlers and tools MUST NEVER trust client- or
model-supplied tenant/department/role fields.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Role = Literal["user", "admin"]


@dataclass(frozen=True, slots=True)
class Principal:
    user_id: str
    tenant_id: str
    role: Role
    departments: set[str]
    correlation_id: str

    def has_department_access(self, department: str) -> bool:
        """Check if principal is authorized for a given department."""
        return "General" in self.departments or department in self.departments

    def is_admin(self) -> bool:
        return self.role == "admin"
