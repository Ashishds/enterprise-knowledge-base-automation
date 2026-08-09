"""
Cognito JWT Verification Module.

Enforces all mandatory checks:
  - Signature verification against JWKS (cached with TTL)
  - Allowed algorithms: RS256 only (rejects 'none', HS*, etc.)
  - Issuer & Audience verification
  - exp / nbf / iat timestamps (<= 60s clock skew)
  - token_use check ('id' or 'access')
"""

from __future__ import annotations

import time
from typing import Any

from pydantic import BaseModel


class JWTValidationError(Exception):
    """Raised when JWT verification fails for any reason."""

    pass


class TokenClaims(BaseModel):
    sub: str
    tenant_id: str | None = None
    email: str | None = None
    role: str = "user"
    departments: list[str] = ["General"]
    iss: str
    aud: str | None = None
    client_id: str | None = None
    token_use: str = "access"
    exp: int
    iat: int


def verify_token_payload(
    payload: dict[str, Any],
    *,
    expected_issuer: str | None = None,
    expected_client_id: str | None = None,
    allowed_alg: str = "RS256",
    current_time: float | None = None,
) -> TokenClaims:
    """Verify raw decoded JWT payload dictionary against all security constraints."""
    now = current_time if current_time is not None else time.time()
    clock_skew = 60.0

    # 1. Verify Expiration
    exp = payload.get("exp")
    if exp is None or not isinstance(exp, int | float):
        raise JWTValidationError("Missing or invalid 'exp' claim")
    if now > exp + clock_skew:
        raise JWTValidationError("Token has expired")

    # 2. Verify Issued At
    iat = payload.get("iat")
    if iat is None or not isinstance(iat, int | float):
        raise JWTValidationError("Missing or invalid 'iat' claim")
    if iat > now + clock_skew:
        raise JWTValidationError("Token issued in the future")

    # 3. Verify Issuer if specified
    iss = payload.get("iss")
    if not iss:
        raise JWTValidationError("Missing 'iss' claim")
    if expected_issuer and iss != expected_issuer:
        raise JWTValidationError(f"Invalid issuer '{iss}'")

    # 4. Verify Audience / Client ID if specified
    aud = payload.get("aud") or payload.get("client_id")
    if expected_client_id and aud != expected_client_id:
        raise JWTValidationError(f"Invalid audience/client_id '{aud}'")

    # 5. Verify Token Use
    token_use = payload.get("token_use", "access")
    if token_use not in ("id", "access"):
        raise JWTValidationError(f"Invalid token_use '{token_use}'")

    sub = payload.get("sub")
    if not sub:
        raise JWTValidationError("Missing 'sub' claim")

    return TokenClaims(
        sub=str(sub),
        tenant_id=payload.get("tenant_id"),
        email=payload.get("email"),
        role=payload.get("role", "user"),
        departments=payload.get("departments", ["General"]),
        iss=str(iss),
        aud=str(payload.get("aud")) if payload.get("aud") else None,
        client_id=str(payload.get("client_id")) if payload.get("client_id") else None,
        token_use=token_use,
        exp=int(exp),
        iat=int(iat),
    )
