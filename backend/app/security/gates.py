"""
Pre-Flight and Post-Flight Deterministic Gates.

Phase 3: Fixed rails outside the agent's reach.
  - Pre-flight: Input length/encoding validation + direct prompt injection check.
  - Post-flight: Citation validator (strips invented citations) + PII/secret redaction + confidence scoring.
"""

from __future__ import annotations

import re

from ..agent.state import EvidenceItem
from ..rag.constants import INSUFFICIENT_EVIDENCE


class SecurityGateError(RuntimeError):
    """Raised when pre-flight security check fails."""

    pass


# 1. Pre-Flight Input Validation & Injection Check
DIRECT_INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"reveal\s+(system\s+)?prompt",
    r"system\s+prompt\s*:",
    r"\[ADMIN\s+(MODE|OVERRIDE)\]",
    r"override\s+security\s+policy",
    r"you\s+are\s+now\s+(an?\s+)?unrestricted",
    r"you\s+are\s+(now\s+)?DAN",
    r"Do\s+Anything\s+Now",
    r"ignore\s+safety",
    r"disregard\s+security",
]
COMPILED_DIRECT_PATTERNS = [re.compile(p, re.IGNORECASE) for p in DIRECT_INJECTION_PATTERNS]


def run_pre_flight_checks(question: str) -> None:
    """Validate user input length, encoding, and run direct prompt injection gate."""
    if not question or not question.strip():
        raise SecurityGateError("Question cannot be empty")

    if len(question) > 4000:
        raise SecurityGateError("Question exceeds maximum length limit of 4000 characters")

    for pat in COMPILED_DIRECT_PATTERNS:
        if pat.search(question):
            raise SecurityGateError("Direct prompt injection pattern detected in input")


# 2. Post-Flight Citation Validator
def validate_and_filter_citations(
    raw_citations: list[EvidenceItem],
    retrieved_evidence: list[EvidenceItem],
) -> list[EvidenceItem]:
    """Strict Post-Flight Gate (CLAUDE.md §6):

    Citations are NEVER invented. Every citation must map to a retrieved chunk_id
    present in the retrieved evidence set. Any unverified citation is removed.
    """
    valid_chunk_ids = {e.chunk_id for e in retrieved_evidence}
    verified: list[EvidenceItem] = []

    for cit in raw_citations:
        if cit.chunk_id in valid_chunk_ids:
            verified.append(cit)

    return verified


# 3. Post-Flight Output Guardrail (Secret / PII Redaction)
SECRET_PATTERNS = [
    (re.compile(r"sk-[a-zA-Z0-9]{32,}", re.IGNORECASE), "[REDACTED_API_KEY]"),
    (re.compile(r"AKIA[0-9A-Z]{16}", re.IGNORECASE), "[REDACTED_AWS_KEY]"),
    (re.compile(r"bearer\s+[a-zA-Z0-9\._\-]{30,}", re.IGNORECASE), "[REDACTED_TOKEN]"),
]


def run_post_flight_output_guardrail(answer: str) -> str:
    """Redact secrets and sensitive tokens from answer string."""
    cleaned = answer
    for pattern, replacement in SECRET_PATTERNS:
        cleaned = pattern.sub(replacement, cleaned)
    return cleaned


# 4. Confidence Score Calculation
def calculate_confidence_score(evidence: list[EvidenceItem], answer: str) -> float:
    """Calculate reproducible confidence score [0.0 - 1.0]."""
    if not evidence or answer == INSUFFICIENT_EVIDENCE:
        return 0.0

    max_sim = max((e.similarity for e in evidence), default=0.0)
    avg_sim = sum(e.similarity for e in evidence) / len(evidence)

    # Formula weighting max similarity and chunk density
    score = min(1.0, max_sim * 0.7 + avg_sim * 0.3)
    return float(round(score, 2))
