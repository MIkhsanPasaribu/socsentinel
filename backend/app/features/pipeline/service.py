"""
SOCsentinel — Investigation Pipeline service.

Orchestrates the end-to-end investigation workflow:
Alert → Orchestrator → L1 Triage → Evidence Collector → MITRE Mapper →
Threat Scenario (optional) → Detection → Report Writer → Response Planner → Validator.
"""

import time
import uuid
from datetime import datetime
from typing import Any

from app.core.logger import get_logger
from app.shared.schemas import AlertInput, InvestigationStatus, PipelineState
from app.shared.exceptions.base import PipelineError
from app.shared.utils.escalation import determine_escalation_level
from app.shared.database import save_investigation, load_investigation, load_all_investigations

from app.features.orchestrator.service import route_alert
from app.features.triage.service import classify_alert
from app.features.evidence.service import collect_evidence
from app.features.mitre_mapper.service import map_to_attack
from app.features.detection.service import generate_detection
from app.features.threat_generator.service import generate_threat_scenario
from app.features.report_writer.service import generate_report
from app.features.response_planner.service import generate_playbook
from app.features.validator.service import validate_playbook

logger = get_logger(__name__)

# In-memory cache for pipeline state (write-through to SQLite)
_pipeline_store: dict[str, PipelineState] = {}
_store_loaded: bool = False


def _ensure_store_loaded() -> None:
    """Load investigations from SQLite into memory cache on first access."""
    global _store_loaded
    if _store_loaded:
        return
    _store_loaded = True
    try:
        saved = load_all_investigations()
        for inv_id, state_dict in saved.items():
            try:
                _pipeline_store[inv_id] = PipelineState(**state_dict)
            except Exception:
                pass  # Skip corrupted entries
        if saved:
            logger.info(
                "Loaded investigations from database",
                count=len(saved),
            )
    except Exception as e:
        logger.warning("Failed to load investigations from database", error=str(e))


def _persist_state(state: PipelineState) -> None:
    """Persist pipeline state to SQLite (non-blocking best-effort)."""
    try:
        save_investigation(state.investigation_id, state.model_dump())
    except Exception as e:
        logger.warning(
            "Failed to persist investigation",
            investigation_id=state.investigation_id,
            error=str(e),
        )


def _add_audit_entry(
    state: PipelineState,
    step: str,
    result: dict,
    status: str = "completed",
    extra: dict | None = None,
) -> None:
    """Add an audit trail entry to the pipeline state."""
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "step": step,
        "agent": result.get("_agent", step),
        "processing_time_ms": result.get("_processing_time_ms", 0),
        "confidence": result.get("confidence", None),
        "status": status,
    }
    if extra:
        entry.update(extra)
    state.audit_trail.append(entry)


def select_threat_technique_id(
    mitre_result: dict[str, Any],
    override: str | None,
) -> str | None:
    """Pick a technique ID for threat scenario generation."""
    if override:
        return override
    techniques = mitre_result.get("techniques", [])
    for technique in techniques:
        technique_id = technique.get("technique_id") or technique.get("id")
        if technique_id:
            return technique_id
    return None


async def run_investigation(
    alert: AlertInput,
    include_threat_scenario: bool = False,
    threat_technique_id: str | None = None,
) -> PipelineState:
    """Run the full investigation pipeline on an alert.

    Executes all agents sequentially, passing context from each
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

        # Escalation check after triage (L1 → L2)
        classification = triage_result.get("classification", "investigate")
        escalation = determine_escalation_level(
            severity=alert.severity.value,
            triage_classification=classification,
            triage_confidence=triage_result.get("confidence"),
        )
        state.escalation_result = escalation
        state.audit_trail.append({
            "timestamp": datetime.utcnow().isoformat(),
            "step": "escalation_check",
            "agent": "Escalation Engine",
            "level": escalation["level"],
            "reason": escalation["reason"],
            "auto_escalated": escalation["auto_escalated"],
            "status": "completed",
        })

        # Check if triage says to close (false positive)
        if classification == "close":
            logger.info(
                "Alert closed by L1 Triage (false positive)",
                investigation_id=investigation_id,
            )
            state.status = InvestigationStatus.COMPLETED
            state.completed_at = datetime.utcnow().isoformat()
            _pipeline_store[investigation_id] = state
            _persist_state(state)
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

        # Step 4.2: Threat Scenario Generation (optional)
        if include_threat_scenario:
            state.status = InvestigationStatus.GENERATING_THREAT_SCENARIO
            selected_technique = select_threat_technique_id(
                mitre_result,
                threat_technique_id,
            )
            if selected_technique:
                threat_result = await generate_threat_scenario(
                    technique_id=selected_technique,
                    apt_group="generic",
                    additional_context={
                        "source": "pipeline",
                        "alert_id": alert.alert_id,
                    },
                )
                state.threat_scenario = threat_result
                _add_audit_entry(state, "threat_generator", threat_result)
            else:
                _add_audit_entry(
                    state,
                    "threat_generator",
                    {"_agent": "Threat Generator", "confidence": None},
                    status="skipped",
                    extra={"reason": "no_technique_available"},
                )

        # Step 4.5: Detection Rule Generation
        state.status = InvestigationStatus.GENERATING_DETECTION
        detection_result = await generate_detection(
            alert_data=alert.model_dump(),
            mitre_result=mitre_result,
            evidence_result=evidence_result,
        )
        state.detection_result = detection_result
        _add_audit_entry(state, "detection", detection_result)

        # Re-evaluate escalation after MITRE mapping (L2 → L3)
        techniques = mitre_result.get("techniques", [])
        kill_chain = mitre_result.get("kill_chain_phase", "")
        escalation_post_mitre = determine_escalation_level(
            severity=alert.severity.value,
            triage_classification=classification,
            triage_confidence=triage_result.get("confidence"),
            technique_count=len(techniques) if isinstance(techniques, list) else 0,
            kill_chain_phase=kill_chain,
        )
        if escalation_post_mitre["level"] != escalation["level"]:
            state.escalation_result = escalation_post_mitre
            state.audit_trail.append({
                "timestamp": datetime.utcnow().isoformat(),
                "step": "escalation_upgrade",
                "agent": "Escalation Engine",
                "previous_level": escalation["level"],
                "new_level": escalation_post_mitre["level"],
                "reason": escalation_post_mitre["reason"],
                "status": "completed",
            })

        # Step 5: Report Generation
        state.status = InvestigationStatus.GENERATING_REPORT
        report_result = await generate_report(
            alert_data=alert.model_dump(),
            triage_result=triage_result,
            evidence_result=evidence_result,
            mitre_result=mitre_result,
            detection_result=detection_result,
        )
        state.report_result = report_result
        _add_audit_entry(state, "report_writer", report_result)

        # Step 6: Response Planner
        state.status = InvestigationStatus.GENERATING_RESPONSE
        response_result = await generate_playbook(
            alert_data=alert.model_dump(),
            triage_result=triage_result,
            evidence_result=evidence_result,
            mitre_result=mitre_result,
            report_result=report_result,
        )
        state.response_result = response_result
        _add_audit_entry(state, "response_planner", response_result)

        # Step 7: Validator (Critic)
        state.status = InvestigationStatus.VALIDATING
        validator_result = await validate_playbook(
            alert_data=alert.model_dump(),
            playbook_result=response_result,
        )
        state.validator_result = validator_result
        _add_audit_entry(state, "validator", validator_result)

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
        _persist_state(state)

    logger.info(
        "Investigation pipeline completed",
        investigation_id=investigation_id,
        total_time_ms=state.total_processing_time_ms,
        status=state.status.value,
    )

    return state


def get_investigation(investigation_id: str) -> PipelineState | None:
    """Retrieve a pipeline state by investigation ID.

    Checks in-memory cache first, then falls back to SQLite.

    Args:
        investigation_id: The unique investigation ID.

    Returns:
        PipelineState or None if not found.
    """
    _ensure_store_loaded()

    # Check cache first
    if investigation_id in _pipeline_store:
        return _pipeline_store[investigation_id]

    # Fallback to DB
    state_dict = load_investigation(investigation_id)
    if state_dict:
        try:
            state = PipelineState(**state_dict)
            _pipeline_store[investigation_id] = state
            return state
        except Exception:
            return None
    return None


def list_investigations() -> list[dict[str, Any]]:
    """List all investigations with summary info.

    Returns:
        List of investigation summary dicts.
    """
    _ensure_store_loaded()

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
