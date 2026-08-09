from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from ..config import Settings, get_settings
from ..euri_client import (
    EuriAuthError,
    EuriClient,
    EuriPermanentError,
    EuriTransientError,
    get_euri_client,
)
from ..extraction import extract_text
from ..rag_store import RagStore, get_rag_store
from ..schemas import DocumentSummary, UploadResponse

router = APIRouter(prefix="/api/documents", tags=["documents"])


@router.get("", response_model=list[DocumentSummary])
async def list_documents(
    department: str | None = None, store: RagStore = Depends(get_rag_store)
) -> list[DocumentSummary]:
    return [
        DocumentSummary(
            id=d.id,
            filename=d.filename,
            department=d.department,
            chunk_count=len(d.chunks),
            char_count=len(d.text),
            created_at=d.created_at,
        )
        for d in store.list_documents(department)
    ]


@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    department: str = Form(...),
    euri: EuriClient = Depends(get_euri_client),
    store: RagStore = Depends(get_rag_store),
    settings: Settings = Depends(get_settings),
) -> UploadResponse:
    if not settings.euri_api_key:
        raise HTTPException(
            500, "EURI_API_KEY is not configured on the server (see backend/.env.example)."
        )

    content = await file.read()
    if len(content) > settings.max_upload_bytes:
        raise HTTPException(
            413, f"File exceeds the {settings.max_upload_bytes // (1024*1024)}MB local demo limit."
        )

    text = extract_text(file.filename or "upload", content)
    if not text.strip():
        raise HTTPException(422, "No extractable text found in this file.")

    try:
        doc = await store.add_document(euri, file.filename or "upload", department, text)
    except EuriAuthError as exc:
        raise HTTPException(401, str(exc)) from exc
    except (EuriPermanentError, EuriTransientError) as exc:
        raise HTTPException(502, f"Embedding call failed while ingesting: {exc}") from exc

    return UploadResponse(
        document=DocumentSummary(
            id=doc.id,
            filename=doc.filename,
            department=doc.department,
            chunk_count=len(doc.chunks),
            char_count=len(doc.text),
            created_at=doc.created_at,
        )
    )
