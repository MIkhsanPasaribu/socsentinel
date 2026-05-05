"""
SOCsentinel — Level-aware escalation rules engine.

Implements SOC analyst hierarchy escalation logic:
- L1 → L2: Severity >= high, or triage classification = "escalate"
- L2 → L3: MITRE techniques >= 3, or kill chain phase is late-stage
- Auto-close: Triage classification = "close" (false positive)

Maps to UC-06 from the hackathon notes.
"""

from typing import Any

from app.core.logger import get_logger

logger = get_logger(__name__)


class EscalationLevel:
    """SOC analyst level constants."""
    L1 = "L1"
    L2 = "L2"
    L3 = "L3"


# Late-stage kill chain phases that warrant L3 escalation
LATE_STAGE_PHASES = {
    "lateral-movement",
    "collection",
    "command-and-control",
    "exfiltration",
    "impact",
}


def determine_escalation_level(
    severity: str,
    triage_classification: str | None = None,
    triage_confidence: float | None = None,
    technique_count: int = 0,
    kill_chain_phase: str | None = None,
) -> dict[str, Any]:
    """Determine the appropriate SOC analyst escalation level.

    Args:
        severity: Alert severity (critical, high, medium, low, info).
        triage_classification: L1 triage result (investigate, close, escalate).
        triage_confidence: L1 triage confidence score (0-1).
        technique_count: Number of MITRE ATT&CK techniques mapped.
        kill_chain_phase: Detected kill chain phase.

    Returns:
        Dict with level, reason, auto_escalated fields.
    """
    level = EscalationLevel.L1
    reasons: list[str] = []
    auto_escalated = False

    # Rule 1: Auto-close on false positive
    if triage_classification == "close":
        return {
            "level": EscalationLevel.L1,
            "action": "close",
            "reason": "False positive — closed by L1 Triage",
            "auto_escalated": False,
        }

    # Rule 2: Explicit escalation from triage
    if triage_classification == "escalate":
        level = EscalationLevel.L2
        reasons.append("L1 Triage explicitly escalated")
        auto_escalated = True

    # Rule 3: High/Critical severity → auto-escalate to L2
    if severity in ("critical", "high"):
        if level != EscalationLevel.L2:
            level = EscalationLevel.L2
            auto_escalated = True
        reasons.append(f"Severity is {severity}")

    # Rule 4: Low confidence on triage → escalate to L2
    if triage_confidence is not None and triage_confidence < 0.5:
        if level != EscalationLevel.L2:
            level = EscalationLevel.L2
            auto_escalated = True
        reasons.append(f"Low triage confidence ({triage_confidence:.0%})")

    # Rule 5: Multiple MITRE techniques → escalate to L3
    if technique_count >= 3:
        level = EscalationLevel.L3
        reasons.append(f"{technique_count} MITRE ATT&CK techniques detected")
        auto_escalated = True

    # Rule 6: Late-stage kill chain → escalate to L3
    if kill_chain_phase and kill_chain_phase.lower() in LATE_STAGE_PHASES:
        level = EscalationLevel.L3
        reasons.append(f"Late-stage kill chain phase: {kill_chain_phase}")
        auto_escalated = True

    result = {
        "level": level,
        "action": "investigate",
        "reason": "; ".join(reasons) if reasons else "Standard L1 investigation",
        "auto_escalated": auto_escalated,
    }

    if auto_escalated:
        logger.info(
            "Alert auto-escalated",
            level=level,
            reason=result["reason"],
        )

    return result
