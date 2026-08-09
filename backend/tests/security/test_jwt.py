import time

import pytest

from app.auth.jwt import JWTValidationError, verify_token_payload


@pytest.mark.security
def test_jwt_verification_expired_token_raises():
    now = time.time()
    payload = {
        "sub": "user_123",
        "iss": "https://cognito-idp.us-east-1.amazonaws.com/us-east-1_Pool",
        "exp": int(now - 300),  # expired 5 min ago
        "iat": int(now - 600),
    }
    with pytest.raises(JWTValidationError, match="Token has expired"):
        verify_token_payload(payload, current_time=now)


@pytest.mark.security
def test_jwt_verification_wrong_issuer_raises():
    now = time.time()
    payload = {
        "sub": "user_123",
        "iss": "https://malicious-issuer.com",
        "exp": int(now + 3600),
        "iat": int(now),
    }
    with pytest.raises(JWTValidationError, match="Invalid issuer"):
        verify_token_payload(
            payload,
            expected_issuer="https://cognito-idp.us-east-1.amazonaws.com/us-east-1_Pool",
            current_time=now,
        )


@pytest.mark.security
def test_jwt_verification_valid_payload_succeeds():
    now = time.time()
    expected_iss = "https://cognito-idp.us-east-1.amazonaws.com/us-east-1_Pool"
    payload = {
        "sub": "user_123",
        "tenant_id": "tenant_acme",
        "email": "user@acme.com",
        "role": "admin",
        "departments": ["HR", "Finance"],
        "iss": expected_iss,
        "client_id": "client_abc",
        "token_use": "access",
        "exp": int(now + 3600),
        "iat": int(now),
    }
    claims = verify_token_payload(
        payload,
        expected_issuer=expected_iss,
        expected_client_id="client_abc",
        current_time=now,
    )
    assert claims.sub == "user_123"
    assert claims.tenant_id == "tenant_acme"
    assert claims.role == "admin"
    assert "HR" in claims.departments
