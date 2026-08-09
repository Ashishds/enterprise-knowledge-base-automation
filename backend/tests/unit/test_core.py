import pytest
from fastapi.testclient import TestClient

from app.core.errors import RateLimitExceededError
from app.core.rate_limit import InMemoryRateLimiter
from app.main import app

client = TestClient(app)


@pytest.mark.unit
def test_healthz_endpoint():
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.unit
def test_readyz_endpoint():
    from app.config import Settings, get_settings

    # 1. Unconfigured state returns 503 Service Unavailable
    app.dependency_overrides[get_settings] = lambda: Settings(euri_api_key="")
    try:
        response_503 = client.get("/readyz")
        assert response_503.status_code == 503
    finally:
        app.dependency_overrides.clear()

    # 2. Configured state returns 200 OK
    app.dependency_overrides[get_settings] = lambda: Settings(euri_api_key="test_key")
    try:
        response = client.get("/readyz")
        assert response.status_code == 200
        assert response.json()["status"] == "ready"
    finally:
        app.dependency_overrides.clear()


@pytest.mark.unit
def test_correlation_id_middleware():
    response = client.get("/healthz")
    assert "x-correlation-id" in response.headers

    # Custom correlation ID propagation
    custom_id = "test-correlation-12345"
    res_custom = client.get("/healthz", headers={"x-correlation-id": custom_id})
    assert res_custom.headers["x-correlation-id"] == custom_id


@pytest.mark.unit
def test_security_headers_middleware():
    response = client.get("/healthz")
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Strict-Transport-Security"] == "max-age=31536000; includeSubDomains"


@pytest.mark.unit
def test_rate_limiter_exceeded_raises_429():
    limiter = InMemoryRateLimiter()
    # Consume 2 allowed tokens
    limiter.check_rate_limit("user1", limit=2, window_sec=60)
    limiter.check_rate_limit("user1", limit=2, window_sec=60)

    with pytest.raises(RateLimitExceededError) as exc_info:
        limiter.check_rate_limit("user1", limit=2, window_sec=60)

    assert exc_info.value.status_code == 429
    assert exc_info.value.retry_after_sec >= 1
