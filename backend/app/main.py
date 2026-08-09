from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .core.errors import AppError, app_error_handler, generic_exception_handler
from .core.logging import configure_logging
from .core.middleware import CorrelationAndSecurityMiddleware
from .euri_client import get_euri_client
from .routes import chat, documents, health

configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    yield
    await get_euri_client().aclose()


settings = get_settings()

app = FastAPI(
    title="EKBA API (Enterprise Knowledge-Base Automation)",
    description=(
        "Multi-tenant, department-scoped, agentic RAG platform API. "
        "See docs/ARCHITECTURE.md for full specs."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

# Exception handlers
app.add_exception_handler(AppError, app_error_handler)  # type: ignore[arg-type]
app.add_exception_handler(Exception, generic_exception_handler)

# Middlewares
app.add_middleware(
    CorrelationAndSecurityMiddleware,
    max_upload_bytes=settings.max_upload_bytes,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(health.router)
app.include_router(chat.router)
app.include_router(documents.router)


@app.get("/")
async def root() -> dict[str, str]:
    return {"service": "ekba-api", "status": "running", "docs": "/docs"}
