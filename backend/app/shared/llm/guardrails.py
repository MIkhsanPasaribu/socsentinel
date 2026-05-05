"""
SOCsentinel — LLM input/output guardrails.

Validates and sanitizes LLM inputs and outputs to ensure safety,
prevent prompt injection, and filter sensitive information.
"""

import re

from app.core.logger import get_logger

logger = get_logger(__name__)

# Patterns that indicate prompt injection attempts
INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"forget\s+(your|all)\s+instructions",
    r"you\s+are\s+now\s+a",
    r"pretend\s+(you\s+are|to\s+be)",
    r"disregard\s+(all|the)\s+(above|previous)",
    r"override\s+system\s+prompt",
    r"new\s+instructions?\s*:",
]

# Patterns for PII detection
PII_PATTERNS = {
    "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
    "credit_card": r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",
    "email_address": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
}

MAX_INPUT_LENGTH = 15000


def validate_input(text: str) -> tuple[bool, str]:
    """Validate user input before sending to LLM.

    Checks for:
    - Input length limits
    - Prompt injection attempts

    Args:
        text: Raw user input text.

    Returns:
        Tuple of (is_valid, message).
    """
    if not text or not text.strip():
        return False, "Input cannot be empty"

    if len(text) > MAX_INPUT_LENGTH:
        return False, f"Input exceeds maximum length ({MAX_INPUT_LENGTH} characters)"

    # Check for prompt injection
    text_lower = text.lower()
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, text_lower):
            logger.warning(
                "Prompt injection attempt detected",
                pattern=pattern,
                input_preview=text[:100],
            )
            return False, "Invalid input detected"

    return True, "OK"


def validate_output(text: str) -> tuple[bool, str]:
    """Validate LLM output before sending to user.

    Checks for:
    - PII leakage (SSN, credit cards, etc.)
    - Empty responses

    Args:
        text: Raw LLM output text.

    Returns:
        Tuple of (is_valid, sanitized_text).
    """
    if not text or not text.strip():
        return False, "LLM returned empty response"

    # Check for PII
    for pii_type, pattern in PII_PATTERNS.items():
        if re.search(pattern, text):
            logger.warning(
                "PII detected in LLM output",
                pii_type=pii_type,
            )
            # Redact the PII
            text = re.sub(pattern, f"[REDACTED-{pii_type.upper()}]", text)

    return True, text
