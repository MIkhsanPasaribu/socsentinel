"""
SOCsentinel — Feedback loop for self-improving triage.

Stores analyst decisions and uses them to enrich future triage prompts
with historical context about similar alerts. This creates a closed-loop
learning system where analyst corrections improve future AI classifications.
"""

from typing import Any

from app.core.logger import get_logger

logger = get_logger(__name__)

# In-memory feedback store (production: database)
_feedback_store: list[dict[str, Any]] = []


def record_feedback(
    alert_severity: str,
    alert_rule_name: str,
    triage_classification: str,
    analyst_decision: str,
    confidence: float | None = None,
) -> None:
    """Record analyst feedback for future triage improvement.

    Args:
        alert_severity: Original alert severity level.
        alert_rule_name: The SIEM rule that triggered the alert.
        triage_classification: What the AI classified the alert as.
        analyst_decision: What the analyst decided (approve/escalate/reject).
        confidence: AI confidence score at time of triage.
    """
    entry = {
        "severity": alert_severity,
        "rule_name": alert_rule_name,
        "ai_classification": triage_classification,
        "analyst_decision": analyst_decision,
        "confidence": confidence,
    }
    _feedback_store.append(entry)
    logger.info(
        "Feedback recorded for self-improving triage",
        rule_name=alert_rule_name,
        ai_classification=triage_classification,
        analyst_decision=analyst_decision,
    )


def get_relevant_feedback(rule_name: str, limit: int = 3) -> list[dict[str, Any]]:
    """Get recent analyst feedback for similar alerts.

    Retrieves historical analyst decisions for alerts triggered by the
    same SIEM rule, enabling the triage agent to learn from past corrections.

    Args:
        rule_name: The SIEM rule name to find feedback for.
        limit: Maximum number of feedback entries to return.

    Returns:
        List of feedback dicts with severity, ai_classification,
        analyst_decision, and confidence.
    """
    relevant = [
        f for f in _feedback_store
        if f["rule_name"] == rule_name
    ]
    return relevant[-limit:]


def get_feedback_stats() -> dict[str, Any]:
    """Get aggregate feedback statistics.

    Returns:
        Dict with total feedback count, agreement rate, and
        correction breakdown.
    """
    total = len(_feedback_store)
    if total == 0:
        return {
            "total_feedback": 0,
            "agreement_rate": 0.0,
            "corrections": 0,
        }

    # Agreement: analyst approved what AI classified as "investigate"
    agreements = sum(
        1 for f in _feedback_store
        if (f["ai_classification"] == "investigate" and f["analyst_decision"] == "approve")
        or (f["ai_classification"] == "close" and f["analyst_decision"] == "reject")
    )

    return {
        "total_feedback": total,
        "agreement_rate": round(agreements / total * 100, 1),
        "corrections": total - agreements,
    }
