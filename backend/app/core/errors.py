"""
Generic Production Error Handling & Typed Error Codes.

Task 1.4:
  - Standardized error payload structure with correlation_id tracking.
  - Custom application exception hierarchy.
"""

from __future__ import annotations

from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse

from .logging import get_correlation_id


class AppError(Exception):
    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_SERVER_ERROR",
        status_code: int = 500,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}


class AuthenticationError(AppError):
    def __init__(self, message: str = "Authentication failed") -> None:
        super().__init__(message=message, code="AUTHENTICATION_FAILED", status_code=401)


class AuthorizationError(AppError):
    def __init__(self, message: str = "Access denied") -> None:
        super().__init__(message=message, code="AUTHORIZATION_FAILED", status_code=403)


class TenancyError(AppError):
    def __init__(self, message: str = "Tenancy context violation") -> None:
        super().__init__(message=message, code="TENANCY_VIOLATION", status_code=403)


class RateLimitExceededError(AppError):
    def __init__(self, message: str = "Rate limit exceeded", retry_after_sec: int = 60) -> None:
        super().__init__(
            message=message,
            code="RATE_LIMIT_EXCEEDED",
            status_code=429,
            details={"retry_after": retry_after_sec},
        )
        self.retry_after_sec = retry_after_sec


class NotFoundError(AppError):
    def __init__(self, message: str = "Resource not found") -> None:
        super().__init__(message=message, code="NOT_FOUND", status_code=404)


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    headers = {}
    if isinstance(exc, RateLimitExceededError):
        headers["Retry-After"] = str(exc.retry_after_sec)

    return JSONResponse(
        status_code=exc.status_code,
        headers=headers,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "correlation_id": get_correlation_id(),
                "details": exc.details,
            }
        },
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred",
                "correlation_id": get_correlation_id(),
            }
        },
    )
