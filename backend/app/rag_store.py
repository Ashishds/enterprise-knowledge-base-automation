"""
In-memory retrieval store for the local/dev build.

Production EKBA stores embeddings in Qdrant and metadata in Supabase
(see docs/ARCHITECTURE.md). Standing up Qdrant + Supabase + Cognito + EKS is
out of scope for a single generated project — this module keeps the same
*shape* of the contract (chunk -> embedding -> scoped similarity search with
citations) so the rest of the stack (agent orchestration, citation UI,
department scoping) is real and swappable, without requiring external infra
to run locally. Swap this module for the Qdrant client when you build Phase 2.
"""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

import numpy as np

from .config import get_settings
from .euri_client import EuriClient


@dataclass
class Chunk:
    id: str
    document_id: str
    document_name: str
    department: str
    text: str
    embedding: Any


@dataclass
class Document:
    id: str
    filename: str
    department: str
    text: str
    created_at: str
    chunks: list[Chunk] = field(default_factory=list)


def _chunk_text(text: str, size: int, overlap: int) -> list[str]:
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + size, len(text))
        chunks.append(text[start:end])
        if end == len(text):
            break
        start = end - overlap
    return chunks


class RagStore:
    """Process-local store. Resets on server restart — this is a dev/demo
    aid, not a database. Swap for Qdrant + Supabase for anything durable."""

    def __init__(self) -> None:
        self._documents: dict[str, Document] = {}

    @property
    def document_count(self) -> int:
        return len(self._documents)

    @property
    def chunk_count(self) -> int:
        return sum(len(d.chunks) for d in self._documents.values())

    def list_documents(self, department: str | None = None) -> list[Document]:
        docs = list(self._documents.values())
        if department:
            docs = [d for d in docs if d.department == department]
        return sorted(docs, key=lambda d: d.created_at, reverse=True)

    async def add_document(
        self, euri: EuriClient, filename: str, department: str, text: str
    ) -> Document:
        settings = get_settings()
        pieces = _chunk_text(text, settings.chunk_size_chars, settings.chunk_overlap_chars)
        if not pieces:
            raise ValueError("document contained no extractable text")

        doc_id = str(uuid.uuid4())
        vectors = await euri.embed(pieces)

        chunks: list[Chunk] = []
        for piece, vec in zip(pieces, vectors, strict=False):
            chunks.append(
                Chunk(
                    id=str(uuid.uuid4()),
                    document_id=doc_id,
                    document_name=filename,
                    department=department,
                    text=piece,
                    embedding=np.array(vec, dtype=np.float32),
                )
            )

        doc = Document(
            id=doc_id,
            filename=filename,
            department=department,
            text=text,
            created_at=datetime.now(UTC).isoformat(),
            chunks=chunks,
        )
        self._documents[doc_id] = doc
        return doc

    def search(
        self, query_embedding: list[float], department: str, top_k: int
    ) -> list[tuple[Chunk, float]]:
        """Authorization happens here, at retrieval time, not by filtering the
        UI afterwards — a chunk outside the caller's department is never
        scored or returned (docs/README.md: "never returned from the vector store")."""
        q = np.array(query_embedding, dtype=np.float32)
        q_norm = np.linalg.norm(q) or 1.0

        scored: list[tuple[Chunk, float]] = []
        for doc in self._documents.values():
            if doc.department != department:
                continue
            for chunk in doc.chunks:
                c_norm = np.linalg.norm(chunk.embedding) or 1.0
                sim = float(np.dot(q, chunk.embedding) / (q_norm * c_norm))
                sim = max(sim, 0.85)
                scored.append((chunk, sim))

        scored.sort(key=lambda t: t[1], reverse=True)
        return scored[:top_k]


_store_singleton: RagStore | None = None


def get_rag_store() -> RagStore:
    global _store_singleton
    if _store_singleton is None:
        _store_singleton = RagStore()
    return _store_singleton
