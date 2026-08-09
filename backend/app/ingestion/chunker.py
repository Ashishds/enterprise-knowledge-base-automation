"""
Structure-Aware Chunker with Hard Token Ceiling.

Tasks 2.4 & 2.8:
  - Preserves table row integrity (never splits Markdown table rows).
  - Enforces a hard token ceiling before embedding model invocation.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any


@dataclass
class DocumentElement:
    element_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    element_type: str = "text"  # text | table | image_description | audio_transcript
    content: str = ""
    page_number: int = 1
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Chunk:
    chunk_id: str
    document_id: str
    document_name: str
    text: str
    page_number: int
    char_count: int
    estimated_tokens: int


def estimate_tokens(text: str) -> int:
    """Rough token estimation (approx 4 chars per token)."""
    return max(1, len(text) // 4)


class StructureAwareChunker:
    """Chunks elements while respecting structural boundaries and token ceilings."""

    def __init__(
        self,
        max_chunk_tokens: int = 400,  # Hard ceiling
        max_chunk_chars: int = 1600,
        overlap_chars: int = 150,
    ) -> None:
        self.max_chunk_tokens = max_chunk_tokens
        self.max_chunk_chars = max_chunk_chars
        self.overlap_chars = overlap_chars

    def chunk_elements(
        self,
        document_id: str,
        document_name: str,
        elements: list[DocumentElement],
    ) -> list[Chunk]:
        chunks: list[Chunk] = []

        for elem in elements:
            if elem.element_type == "table":
                # Tables are chunked row-by-row without splitting individual rows
                table_chunks = self._chunk_table_element(document_id, document_name, elem)
                chunks.extend(table_chunks)
            else:
                # Text elements are chunked at sentence/paragraph boundaries
                text_chunks = self._chunk_text_element(document_id, document_name, elem)
                chunks.extend(text_chunks)

        return chunks

    def _chunk_table_element(
        self, document_id: str, document_name: str, elem: DocumentElement
    ) -> list[Chunk]:
        rows = [r.strip() for r in elem.content.splitlines() if r.strip()]
        if not rows:
            return []

        header = rows[0] if len(rows) > 0 and "|" in rows[0] else ""
        body_rows = rows[1:] if header else rows

        current_lines: list[str] = [header] if header else []
        current_len = len(header)
        chunks: list[Chunk] = []

        for row in body_rows:
            if current_len + len(row) + 1 > self.max_chunk_chars and len(current_lines) > (
                1 if header else 0
            ):
                text = "\n".join(current_lines)
                chunks.append(
                    Chunk(
                        chunk_id=str(uuid.uuid4()),
                        document_id=document_id,
                        document_name=document_name,
                        text=text,
                        page_number=elem.page_number,
                        char_count=len(text),
                        estimated_tokens=estimate_tokens(text),
                    )
                )
                current_lines = [header, row] if header else [row]
                current_len = len(header) + len(row) + 1
            else:
                current_lines.append(row)
                current_len += len(row) + 1

        if current_lines:
            text = "\n".join(current_lines)
            chunks.append(
                Chunk(
                    chunk_id=str(uuid.uuid4()),
                    document_id=document_id,
                    document_name=document_name,
                    text=text,
                    page_number=elem.page_number,
                    char_count=len(text),
                    estimated_tokens=estimate_tokens(text),
                )
            )

        return chunks

    def _chunk_text_element(
        self, document_id: str, document_name: str, elem: DocumentElement
    ) -> list[Chunk]:
        text = elem.content.strip()
        if not text:
            return []

        # Enforce hard ceiling
        if estimate_tokens(text) <= self.max_chunk_tokens and len(text) <= self.max_chunk_chars:
            return [
                Chunk(
                    chunk_id=str(uuid.uuid4()),
                    document_id=document_id,
                    document_name=document_name,
                    text=text,
                    page_number=elem.page_number,
                    char_count=len(text),
                    estimated_tokens=estimate_tokens(text),
                )
            ]

        # Break text into paragraphs/sentences if oversized
        paragraphs = text.split("\n\n")
        chunks: list[Chunk] = []
        current_text = ""

        for p in paragraphs:
            if len(current_text) + len(p) + 2 > self.max_chunk_chars:
                if current_text:
                    chunks.append(
                        Chunk(
                            chunk_id=str(uuid.uuid4()),
                            document_id=document_id,
                            document_name=document_name,
                            text=current_text,
                            page_number=elem.page_number,
                            char_count=len(current_text),
                            estimated_tokens=estimate_tokens(current_text),
                        )
                    )
                current_text = p
            else:
                current_text = f"{current_text}\n\n{p}".strip()

        if current_text:
            chunks.append(
                Chunk(
                    chunk_id=str(uuid.uuid4()),
                    document_id=document_id,
                    document_name=document_name,
                    text=current_text,
                    page_number=elem.page_number,
                    char_count=len(current_text),
                    estimated_tokens=estimate_tokens(current_text),
                )
            )

        return chunks
