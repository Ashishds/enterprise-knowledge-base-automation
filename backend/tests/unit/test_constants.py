import pytest

from app.rag.constants import INSUFFICIENT_EVIDENCE


@pytest.mark.unit
def test_insufficient_evidence_refusal_string_is_byte_exact():
    expected = "I could not find enough evidence in the approved documents to answer this question."
    assert INSUFFICIENT_EVIDENCE == expected
    assert len(INSUFFICIENT_EVIDENCE) == len(expected)
