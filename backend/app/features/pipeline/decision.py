"""
SOCsentinel — Human-in-the-Loop decision endpoint.

Records analyst decisions (approve/escalate/reject) on completed
investigations. Maps to UC-05 from the hackathon use cases.
"""

from datetime import datetime
from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel, Field, model_validator

from app.core.logger import get_logger
from app.shared.schemas import APIResponse, InvestigationStatus
from app.shared.exceptions.base import NotFoundError
from app.features.pipeline.service import _pipeline_store, get_investigation
from app.features.pipeline.feedback import record_feedback, get_relevant_feedback, get_feedback_stats

logger = get_logger(__name__)

router = APIRouter(prefix="/pipeline", tags=["Human-in-the-Loop"])


class DecisionRequest(BaseModel):
    """Analyst decision on an investigation."""
    decision: Literal["approve", "escalate", "reject"]
    analyst_notes: str = ""
    confidence_override: float | None = Field(None, ge=0.0, le=1.0)
    severity_override: str | None = None

    @model_validator(mode="after")
    def validate_notes(self) -> "DecisionRequest":
        """Require notes for escalation or rejection."""
        if self.decision in {"escalate", "reject"} and not self.analyst_notes.strip():
            raise ValueError("Analyst notes are required for escalation or rejection")
        if self.confidence_override is not None and not self.analyst_notes.strip():
            raise ValueError("Analyst notes are required when overriding confidence")
        return self


@router.post("/decision/{investigation_id}", response_model=APIResponse)
async def record_decision(investigation_id: str, req: DecisionRequest) -> APIResponse:
    """Record an analyst's decision on a completed investigation.

    This implements the Human-in-the-Loop requirement (UC-05):
    analysts review the AI-generated investigation and make
    a final decision: approve, escalate, or reject.

    The decision is recorded in the audit trail for full traceability.

    Args:
        investigation_id: The investigation to decide on.
        req: Decision payload with type and optional notes.
    """
    state = get_investigation(investigation_id)
    if not state:
        raise NotFoundError("Investigation", investigation_id)

    # Ensure state is in memory store for persistence
    _pipeline_store[investigation_id] = state

    # Record decision
    decision_record = {
        "decision": req.decision,
        "analyst_notes": req.analyst_notes,
        "decided_at": datetime.utcnow().isoformat() + "Z",
        "investigation_status_at_decision": state.status.value,
        "confidence_override": req.confidence_override,
        "severity_override": req.severity_override,
    }

    state.analyst_decision = decision_record  # type: ignore[attr-defined]

    # Add to audit trail
    audit_entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "step": "human_decision",
        "agent": "Human Analyst",
        "action": req.decision,
        "analyst_notes": req.analyst_notes,
        "status": "completed",
    }
    if req.confidence_override is not None:
        audit_entry["confidence_override"] = req.confidence_override
    if req.severity_override:
        audit_entry["severity_override"] = req.severity_override
    state.audit_trail.append(audit_entry)

    # Update status based on decision
    if req.decision == "reject":
        state.status = InvestigationStatus.FAILED
    elif req.decision == "escalate":
        # Keep as completed but mark escalation in audit
        state.audit_trail.append({
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "step": "l3_escalation",
            "agent": "Human Analyst",
            "action": "escalated_to_l3",
            "reason": req.analyst_notes or "Manual L3 escalation",
            "status": "completed",
        })

    logger.info(
        "Analyst decision recorded",
        investigation_id=investigation_id,
        decision=req.decision,
        notes=req.analyst_notes[:100] if req.analyst_notes else "",
    )

    # Record feedback for self-improving triage loop
    triage_classification = ""
    triage_confidence: float | None = None
    if state.triage_result:
        triage_classification = state.triage_result.get("classification", "")
        triage_confidence = state.triage_result.get("confidence")

    record_feedback(
        alert_severity=state.alert.severity.value,
        alert_rule_name=state.alert.rule_name,
        triage_classification=triage_classification,
        analyst_decision=req.decision,
        confidence=triage_confidence,
    )

    return APIResponse(
        success=True,
        message=f"Decision '{req.decision}' recorded for {investigation_id}",
        data={
            "investigation_id": investigation_id,
            "decision": req.decision,
            "decided_at": decision_record["decided_at"],
            "confidence_override": req.confidence_override,
            "severity_override": req.severity_override,
        },
    )


@router.get("/risk-summary/{investigation_id}", response_model=APIResponse)
async def get_risk_summary(investigation_id: str) -> APIResponse:
    """Generate a risk summary from investigation results.

    Provides an at-a-glance risk assessment for the analyst workbench,
    including severity, confidence, kill chain position, IOC count,
    MITRE technique count, and recommended action.
    """
    state = get_investigation(investigation_id)
    if not state:
        raise NotFoundError("Investigation", investigation_id)

    # Extract key metrics
    triage = state.triage_result or {}
    evidence = state.evidence_result or {}
    mitre = state.mitre_result or {}
    response = getattr(state, "response_result", None) or {}
    escalation = state.escalation_result or {}

    classification = triage.get("classification", "unknown")
    confidence = triage.get("confidence", 0)
    techniques = mitre.get("techniques", [])
    iocs = evidence.get("iocs", [])
    kill_chain_phase = mitre.get("kill_chain_phase", "unknown")

    # Determine risk level
    risk_score = 0
    if state.alert.severity.value in {"critical", "high"}:
        risk_score += 3
    elif state.alert.severity.value == "medium":
        risk_score += 2
    else:
        risk_score += 1
    risk_score += min(len(techniques), 3)
    if classification == "escalate":
        risk_score += 2
    risk_level = "critical" if risk_score >= 7 else "high" if risk_score >= 5 else "medium" if risk_score >= 3 else "low"

    # Recommended action from response planner
    recommended_action = "Review investigation details"
    if response and isinstance(response, dict):
        steps = response.get("containment_steps", response.get("steps", []))
        if steps and isinstance(steps, list) and len(steps) > 0:
            first = steps[0]
            recommended_action = first if isinstance(first, str) else first.get("action", recommended_action)

    # Decision history for similar alerts
    history = get_relevant_feedback(state.alert.rule_name, limit=5)

    summary = {
        "investigation_id": investigation_id,
        "risk_level": risk_level,
        "risk_score": risk_score,
        "severity": state.alert.severity.value,
        "classification": classification,
        "confidence": confidence,
        "technique_count": len(techniques),
        "top_techniques": [t.get("technique_id", t.get("id", "?")) for t in techniques[:3]],
        "ioc_count": len(iocs) if isinstance(iocs, list) else 0,
        "kill_chain_phase": kill_chain_phase,
        "escalation_level": escalation.get("level", "L1"),
        "recommended_action": recommended_action,
        "decision_history": history,
        "has_past_decisions": len(history) > 0,
    }

    return APIResponse(
        success=True,
        message=f"Risk summary for {investigation_id}",
        data=summary,
    )


@router.get("/feedback-stats", response_model=APIResponse)
async def feedback_stats_endpoint() -> APIResponse:
    """Get aggregate feedback statistics for the self-improving triage loop."""
    stats = get_feedback_stats()
    return APIResponse(
        success=True,
        message="Feedback loop statistics",
        data=stats,
    )
