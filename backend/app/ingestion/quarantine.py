"""
Indirect Prompt Injection Scanner & Document Quarantine Path.

Task 2.9:
  - Scans document text elements for indirect prompt injection attack vectors.
  - Quarantines infected elements and logs audit events before vector indexing.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior)\s+instructions",
    r"system\s+prompt\s*:",
    r"you\s+are\s+now\s+(an?\s+)?unrestricted",
    r"\[ADMIN\s+OVERRIDE\]",
    r"<\|im_start\|>",
    r"<\|im_end\|>",
    r"eval\s*\(\s*.*?\s*\)",
    r"exec\s*\(\s*.*?\s*\)",
    r"disregard\s+the\s+above",
    r"developer\s+mode\s+enabled",
]

COMPILED_PATTERNS = [re.compile(p, re.IGNORECASE) for p in INJECTION_PATTERNS]


@dataclass
class QuarantineResult:
    is_flagged: bool
    reason: str | None = None
    matched_pattern: str | None = None


def scan_text_for_injection(text: str) -> QuarantineResult:
    """Scan string content against indirect prompt injection patterns."""
    if not text:
        return QuarantineResult(is_flagged=False)

    for pattern in COMPILED_PATTERNS:
        match = pattern.search(text)
        if match:
            return QuarantineResult(
                is_flagged=True,
                reason=f"Matched prompt injection heuristic pattern: '{match.group(0)}'",
                matched_pattern=pattern.pattern,
            )

    return QuarantineResult(is_flagged=False)
