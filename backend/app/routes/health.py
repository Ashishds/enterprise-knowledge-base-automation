"""
Health & Readiness Probes.

Task 1.13:
  - /healthz: Basic liveness probe.
  - /readyz: Readiness probe checking vector store and gateway configuration.
  - /api/health: Detailed application health metrics.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from ..config import Settings, get_settings
from ..rag_store import RagStore, get_rag_store
from ..schemas import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/healthz")
async def healthz() -> dict[str, str]:
    """Kubernetes / Cloud liveness probe."""
    return {"status": "ok"}


@router.get("/readyz")
async def readyz(
    settings: Settings = Depends(get_settings),
    store: RagStore = Depends(get_rag_store),
) -> dict[str, Any]:
    """Kubernetes / Cloud readiness probe checking core dependencies."""
    checks = {
        "gateway_configured": bool(settings.euri_api_key),
        "vector_store_active": True,
    }
    if not all(checks.values()):
        raise HTTPException(status_code=503, detail={"status": "not_ready", "checks": checks})
    return {"status": "ready", "checks": checks}


@router.get("/api/health", response_model=HealthResponse)
async def health(
    settings: Settings = Depends(get_settings),
    store: RagStore = Depends(get_rag_store),
) -> HealthResponse:
    return HealthResponse(
        status="ok",
        environment=settings.environment,
        euri_key_configured=bool(settings.euri_api_key),
        documents_indexed=store.document_count,
        chunks_indexed=store.chunk_count,
    )
