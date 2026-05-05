"""
SOCsentinel — Confidence scoring utilities.

Provides helper functions for agent confidence scoring
and evidence chain formatting.
"""

from enum import Enum


class ConfidenceLevel(str, Enum):
    """Human-readable confidence levels mapped from numeric scores."""
    VERY_HIGH = "very_high"    # 0.9 - 1.0
    HIGH = "high"              # 0.7 - 0.89
    MEDIUM = "medium"          # 0.5 - 0.69
    LOW = "low"                # 0.3 - 0.49
    VERY_LOW = "very_low"      # 0.0 - 0.29


def score_to_level(score: float) -> ConfidenceLevel:
    """Convert a numeric confidence score to a human-readable level.

    Args:
        score: Confidence score between 0.0 and 1.0.

    Returns:
        ConfidenceLevel enum value.

    Raises:
        ValueError: If score is not between 0.0 and 1.0.
    """
    if not 0.0 <= score <= 1.0:
        raise ValueError(f"Confidence score must be between 0.0 and 1.0, got {score}")

    if score >= 0.9:
        return ConfidenceLevel.VERY_HIGH
    elif score >= 0.7:
        return ConfidenceLevel.HIGH
    elif score >= 0.5:
        return ConfidenceLevel.MEDIUM
    elif score >= 0.3:
        return ConfidenceLevel.LOW
    else:
        return ConfidenceLevel.VERY_LOW


def format_evidence_chain(steps: list[dict]) -> str:
    """Format a list of reasoning steps into a readable evidence chain.

    Args:
        steps: List of dicts with 'step', 'observation', and 'conclusion' keys.

    Returns:
        Formatted evidence chain string.
    """
    if not steps:
        return "No evidence chain available."

    lines = ["Evidence Chain:"]
    for i, step in enumerate(steps, 1):
        lines.append(f"  [{i}] {step.get('step', 'Unknown step')}")
        if observation := step.get("observation"):
            lines.append(f"      Observation: {observation}")
        if conclusion := step.get("conclusion"):
            lines.append(f"      Conclusion: {conclusion}")

    return "\n".join(lines)
