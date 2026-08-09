"""Best-effort text extraction for uploaded files.

Production ingestion (docs/ARCHITECTURE.md, docs/INTEGRATIONS-EURI.md §3) is a
full pipeline: PDF/DOCX/XLSX/PPTX parsing, OCR, vision-model descriptions for
images/diagrams, transcription for audio/video, all bridged to text before
embedding (the embedding model is text-only). This module covers the
practical subset — text, markdown, PDF, DOCX — so the app is genuinely
useful locally without pulling in the full media pipeline.
"""

from __future__ import annotations

import io

from fastapi import HTTPException


def extract_text(filename: str, content: bytes) -> str:
    lower = filename.lower()

    if lower.endswith((".txt", ".md", ".csv")):
        return content.decode("utf-8", errors="replace")

    if lower.endswith(".pdf"):
        try:
            from pypdf import PdfReader
        except ImportError as exc:  # pragma: no cover
            raise HTTPException(500, "pypdf is not installed on the server") from exc
        reader = PdfReader(io.BytesIO(content))
        return "\n".join(page.extract_text() or "" for page in reader.pages)

    if lower.endswith(".docx"):
        try:
            import docx
        except ImportError as exc:  # pragma: no cover
            raise HTTPException(500, "python-docx is not installed on the server") from exc
        document = docx.Document(io.BytesIO(content))
        return "\n".join(p.text for p in document.paragraphs)

    raise HTTPException(
        415,
        f"Unsupported file type for '{filename}'. This local build supports "
        ".txt, .md, .csv, .pdf and .docx. Images, audio and video require the "
        "vision/transcription bridge described in docs/INTEGRATIONS-EURI.md §3, "
        "which is out of scope for this scaffold.",
    )
