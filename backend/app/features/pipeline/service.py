"""
SOCsentinel — Investigation Pipeline service.

Orchestrates the end-to-end investigation workflow:
Alert → Orchestrator → L1 Triage → Evidence Collector → MITRE Mapper → Report Writer.
"""

import time
import uuid
from datetime import datetime
from typing import Any

from app.core.logger import get_logger
from app.shared.schemas import AlertInput, InvestigationStatus, PipelineState
from app.shared.exceptions.base import PipelineError

from app.features.orchestrator.service import route_alert
from app.features.triage.service import classify_alert
from app.features.evidence.service import collect_evidence
from app.features.mitre_mapper.service import map_to_attack
from app.features.report_writer.service import generate_report

logger = get_logger(__name__)

# In-memory store for pipeline state (production would use a database)
_pipeline_store: dict[str, PipelineState] = {}


def _add_audit_entry(state: PipelineState, step: str, result: dict) -> None:
    """Add an audit trail entry to the pipeline state."""
    state.audit_trail.append({
        "timestamp": datetime.utcnow().isoformat(),
        "step": step,
        "agent": result.get("_agent", step),
        "processing_time_ms": result.get("_processing_time_ms", 0),
        "confidence": result.get("confidence", None),
        "status": "completed",
    })


async def run_investigation(alert: AlertInput) -> PipelineState:
    """Run the full investigation pipeline on an alert.

    Executes all 5 agents sequentially, passing context from each
    to the next. Records audit trail and timing throughout.

    Args:
        alert: The SIEM alert to investigate.

    Returns:
        PipelineState with all agent results and audit trail.
    """
    investigation_id = f"INV-{uuid.uuid4().hex[:8].upper()}"
    pipeline_start = time.time()

    state = PipelineState(
        investigation_id=investigation_id,
        alert=alert,
        status=InvestigationStatus.PENDING,
    )

    # Ensure alert has an ID
    if not alert.alert_id:
        alert.alert_id = f"ALERT-{uuid.uuid4().hex[:8].upper()}"

    logger.info(
        "Investigation pipeline started",
        investigation_id=investigation_id,
        alert_id=alert.alert_id,
    )

    try:
        # Step 1: Orchestrator — route and prioritize
        state.status = InvestigationStatus.TRIAGING
        orchestrator_result = await route_alert(alert)
        state.orchestrator_result = orchestrator_result
        _add_audit_entry(state, "orchestrator", orchestrator_result)

        # Step 2: L1 Triage — classify
        triage_result = await classify_alert(alert, orchestrator_context=orchestrator_result)
        state.triage_result = triage_result
        _add_audit_entry(state, "l1_triage", triage_result)

        # Check if triage says to close (false positive)
        classification = triage_result.get("classification", "investigate")
        if classification == "close":
            logger.info(
                "Alert closed by L1 Triage (false positive)",
                investigation_id=investigation_id,
            )
            state.status = InvestigationStatus.COMPLETED
            state.completed_at = datetime.utcnow().isoformat()
            state.total_processing_time_ms = (time.time() - pipeline_start) * 1000
            _pipeline_store[investigation_id] = state
            return state

        # Step 3: Evidence Collection
        state.status = InvestigationStatus.COLLECTING_EVIDENCE
        evidence_result = await collect_evidence(alert, triage_context=triage_result)
        state.evidence_result = evidence_result
        _add_audit_entry(state, "evidence_collector", evidence_result)

        # Step 4: MITRE Mapping
        state.status = InvestigationStatus.MAPPING_MITRE
        mitre_result = await map_to_attack(alert, evidence_context=evidence_result)
        state.mitre_result = mitre_result
        _add_audit_entry(state, "mitre_mapper", mitre_result)

        # Step 5: Report Generation
        state.status = InvestigationStatus.GENERATING_REPORT
        report_result = await generate_report(
            alert_data=alert.model_dump(),
            triage_result=triage_result,
            evidence_result=evidence_result,
            mitre_result=mitre_result,
        )
        state.report_result = report_result
        _add_audit_entry(state, "report_writer", report_result)

        # Complete
        state.status = InvestigationStatus.COMPLETED
        state.completed_at = datetime.utcnow().isoformat()

    except Exception as e:
        state.status = InvestigationStatus.FAILED
        state.completed_at = datetime.utcnow().isoformat()
        state.audit_trail.append({
            "timestamp": datetime.utcnow().isoformat(),
            "step": "pipeline_error",
            "error": str(e),
            "status": "failed",
        })
        logger.error(
            "Investigation pipeline failed",
            investigation_id=investigation_id,
            error=str(e),
        )
        raise PipelineError(
            step=state.status.value,
            message=str(e),
        ) from e
    finally:
        state.total_processing_time_ms = round((time.time() - pipeline_start) * 1000, 1)
        _pipeline_store[investigation_id] = state

    logger.info(
        "Investigation pipeline completed",
        investigation_id=investigation_id,
        total_time_ms=state.total_processing_time_ms,
        status=state.status.value,
    )

    return state


def get_investigation(investigation_id: str) -> PipelineState | None:
    """Retrieve a pipeline state by investigation ID.

    Args:
        investigation_id: The unique investigation ID.

    Returns:
        PipelineState or None if not found.
    """
    return _pipeline_store.get(investigation_id)


def list_investigations() -> list[dict[str, Any]]:
    """List all investigations with summary info.

    Returns:
        List of investigation summary dicts.
    """
    summaries = []
    for inv_id, state in _pipeline_store.items():
        summaries.append({
            "investigation_id": inv_id,
            "alert_id": state.alert.alert_id,
            "status": state.status.value,
            "severity": state.alert.severity.value,
            "started_at": state.started_at,
            "completed_at": state.completed_at,
            "processing_time_ms": state.total_processing_time_ms,
        })
    return summaries
