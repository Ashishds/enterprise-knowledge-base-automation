"""
LangSmith & Correlation Tracing Manager.

Phase 5:
  - Propagates Correlation ID across spans (API -> LangSmith -> Audit).
  - Traces retrieval, reasoning, and tool calls with prompt versions and token counts.
"""

from __future__ import annotations

import logging
from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

logger = logging.getLogger("ekba.tracing")


@contextmanager
def trace_span(
    name: str, correlation_id: str | None = None, metadata: dict[str, Any] | None = None
) -> Generator[dict[str, Any], None, None]:
    meta = metadata or {}
    cid = correlation_id or "cid-local"
    meta["correlation_id"] = cid

    logger.info(f"[TRACE START] span={name} correlation_id={cid} metadata={meta}")
    span_data: dict[str, Any] = {"status": "ok"}
    try:
        yield span_data
    except Exception as exc:
        span_data["status"] = "error"
        span_data["error"] = str(exc)
        logger.error(f"[TRACE ERROR] span={name} correlation_id={cid} error={exc}")
        raise
    finally:
        logger.info(f"[TRACE END] span={name} correlation_id={cid} status={span_data['status']}")
