"""
Security Headers & Correlation ID Middleware.

Tasks 1.2 & 1.3:
  - Generates or propagates X-Correlation-ID for request tracing.
  - Adds mandatory security headers (HSTS, nosniff, DENY frame options).
  - Enforces body-size limit (413 if content-length > max_upload_bytes).
"""

from __future__ import annotations

import uuid
from collections.abc import Awaitable, Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from .logging import set_correlation_id


class CorrelationAndSecurityMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, max_upload_bytes: int = 15 * 1024 * 1024) -> None:
        super().__init__(app)
        self.max_upload_bytes = max_upload_bytes

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        # 1. Enforce max body size check if Content-Length header is present
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.max_upload_bytes:
            return Response(
                content='{"error":{"code":"PAYLOAD_TOO_LARGE","message":"Request payload exceeds maximum limit"}}',
                status_code=413,
                media_type="application/json",
            )

        # 2. Extract or generate Correlation ID
        correlation_id = request.headers.get("x-correlation-id") or str(uuid.uuid4())
        set_correlation_id(correlation_id)

        # 3. Process Request
        response: Response = await call_next(request)

        # 4. Attach response headers
        response.headers["x-correlation-id"] = correlation_id
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        return response
