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
from app.features.pipeline.service import _pipeline_store
from app.features.pipeline.feedback import record_feedback

logger = get_logger(__name__)

router = APIRouter(prefix="/pipeline", tags=["Human-in-the-Loop"])


class DecisionRequest(BaseModel):
    """Analyst decision on an investigation."""
    decision: Literal["approve", "escalate", "reject"]
    analyst_notes: str = ""

    @model_validator(mode="after")
    def validate_notes(self) -> "DecisionRequest":
        """Require notes for escalation or rejection."""
        if self.decision in {"escalate", "reject"} and not self.analyst_notes.strip():
            raise ValueError("Analyst notes are required for escalation or rejection")
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
    state = _pipeline_store.get(investigation_id)
    if not state:
        raise NotFoundError("Investigation", investigation_id)

    # Record decision
    decision_record = {
        "decision": req.decision,
        "analyst_notes": req.analyst_notes,
        "decided_at": datetime.utcnow().isoformat(),
        "investigation_status_at_decision": state.status.value,
    }

    state.analyst_decision = decision_record  # type: ignore[attr-defined]

    # Add to audit trail
    state.audit_trail.append({
        "timestamp": datetime.utcnow().isoformat(),
        "step": "human_decision",
        "agent": "Human Analyst",
        "action": req.decision,
        "analyst_notes": req.analyst_notes,
        "status": "completed",
    })

    # Update status based on decision
    if req.decision == "reject":
        state.status = InvestigationStatus.FAILED
    elif req.decision == "escalate":
        # Keep as completed but mark escalation in audit
        state.audit_trail.append({
            "timestamp": datetime.utcnow().isoformat(),
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
        },
    )
