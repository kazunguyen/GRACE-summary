"""
GRACE Strict Prediction Parser Module
Compliant with evaluation_contract_v2 (parser: exact_last_line_binary_v1).

CRITICAL RULE:
  - If the last non-empty line is exactly "1", returns 1 (Valid Vulnerable).
  - If the last non-empty line is exactly "0", returns 0 (Valid Non-vulnerable).
  - Any other response (empty, words, code fences, unparseable) returns None (Invalid).
  - NEVER coerce invalid responses into 0 or 1!
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ParseResult:
    prediction: Optional[int]
    parse_status: str  # "valid" | "invalid"
    parse_method: str


def parse_prediction(response_text: str) -> ParseResult:
    """Strictly parses the exact binary label from the last non-empty line."""
    if not isinstance(response_text, str) or not response_text.strip():
        return ParseResult(None, "invalid", "empty_response")

    # Iterate lines in reverse to find the last non-empty line
    lines = [line.strip() for line in response_text.splitlines() if line.strip()]
    if not lines:
        return ParseResult(None, "invalid", "empty_response")

    last_line = lines[-1]

    if last_line == "1":
        return ParseResult(1, "valid", "exact_last_line_binary")
    elif last_line == "0":
        return ParseResult(0, "valid", "exact_last_line_binary")

    return ParseResult(None, "invalid", "last_line_not_exact_binary")
