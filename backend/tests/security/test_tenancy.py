import pytest

from app.auth.principal import Principal
from app.security.filters import TenancyViolationError, build_tenant_qdrant_filter


@pytest.mark.security
def test_qdrant_filter_raises_if_tenant_id_missing():
    invalid_principal = Principal(
        user_id="usr_123",
        tenant_id="",
        role="user",
        departments={"General"},
        correlation_id="corr_123",
    )
    with pytest.raises(TenancyViolationError, match="CRITICAL SECURITY VIOLATION"):
        build_tenant_qdrant_filter(invalid_principal, department="General")


@pytest.mark.security
def test_qdrant_filter_builds_valid_payload_for_authorized_department():
    principal = Principal(
        user_id="usr_123",
        tenant_id="tenant_acme",
        role="user",
        departments={"HR"},
        correlation_id="corr_123",
    )
    res = build_tenant_qdrant_filter(principal, department="HR")
    assert "must" in res
    must_list = res["must"]
    assert {"key": "tenant_id", "match": {"value": "tenant_acme"}} in must_list
    assert {"key": "status", "match": {"value": "active"}} in must_list
    assert {"key": "department", "match": {"value": "HR"}} in must_list


@pytest.mark.security
def test_qdrant_filter_raises_if_department_not_authorized():
    principal = Principal(
        user_id="usr_123",
        tenant_id="tenant_acme",
        role="user",
        departments={"HR"},
        correlation_id="corr_123",
    )
    with pytest.raises(TenancyViolationError, match="not authorized for department 'Finance'"):
        build_tenant_qdrant_filter(principal, department="Finance")
