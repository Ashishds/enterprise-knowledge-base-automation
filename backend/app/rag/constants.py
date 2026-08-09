"""
RAG Constants.

Contains the non-negotiable, byte-exact refusal string required by CLAUDE.md §6
and SECURITY.md §5.5. This string MUST NEVER be retyped or modified.
"""

INSUFFICIENT_EVIDENCE = (
    "I could not find enough evidence in the approved documents to answer this question."
)
