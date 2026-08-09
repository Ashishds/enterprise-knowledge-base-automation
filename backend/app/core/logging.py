"""
Structured JSON Logger & Correlation ID propagation.

Injects x-correlation-id into all log output records for end-to-end tracing.
"""

from __future__ import annotations

import contextvars
import json
import logging
import sys
from typing import Any

correlation_id_ctx: contextvars.ContextVar[str] = contextvars.ContextVar(
    "correlation_id", default="none"
)


def get_correlation_id() -> str:
    return correlation_id_ctx.get()


def set_correlation_id(cid: str) -> None:
    correlation_id_ctx.set(cid)


class JSONFormatter(logging.Formatter):
    """Formats log records as structured JSON strings."""

    def format(self, record: logging.LogRecord) -> str:
        log_obj: dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "correlation_id": get_correlation_id(),
        }
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_obj)


def configure_logging(level: int = logging.INFO) -> None:
    """Configure root logger with JSONFormatter."""
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Clear existing handlers
    root_logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    root_logger.addHandler(handler)


logger = logging.getLogger("ekba")
