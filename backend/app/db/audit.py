"""
Append-Only Audit Event Log Writer.

Task 1.11:
  - Records auth, authz, document upload/delete, and guardrail decisions to audit_events.
"""

from __future__ import annotations

import logging
from typing import Any

from sqlalchemy.orm import Session

from ..core.logging import get_correlation_id
from .models import AuditEvent

logger = logging.getLogger("ekba.audit")


def log_audit_event(
    db: Session | None,
    *,
    tenant_id: str,
    actor_id: str,
    action: str,
    resource_type: str,
    resource_id: str,
    outcome: str,  # success | denied | failed
    ip: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> AuditEvent:
    correlation_id = get_correlation_id()
    event = AuditEvent(
        tenant_id=tenant_id,
        actor_id=actor_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        outcome=outcome,
        correlation_id=correlation_id,
        ip=ip,
        metadata_json=metadata or {},
    )

    if db is not None:
        db.add(event)
        db.commit()

    logger.info(
        f"[AUDIT] action={action} actor={actor_id} tenant={tenant_id} outcome={outcome} correlation_id={correlation_id}"
    )
    return event
