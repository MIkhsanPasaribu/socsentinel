"""
SOCsentinel — Server-Sent Events (SSE) for real-time pipeline updates.

Streams agent-by-agent progress as each step completes during an investigation.
Events: agent_started, agent_completed, pipeline_completed, pipeline_failed.
"""

import asyncio
import json
import time
import uuid
from datetime import datetime
from typing import AsyncGenerator

from fastapi import APIRouter
from starlette.responses import StreamingResponse

from app.core.logger import get_logger
from app.shared.schemas import AlertInput, InvestigationStatus, PipelineState
from app.shared.exceptions.base import PipelineError

from app.features.orchestrator.service import route_alert
from app.features.triage.service import classify_alert
from app.features.evidence.service import collect_evidence
from app.features.mitre_mapper.service import map_to_attack
from app.features.detection.service import generate_detection
from app.features.threat_generator.service import generate_threat_scenario
from app.features.report_writer.service import generate_report
from app.features.response_planner.service import generate_playbook
from app.features.pipeline.service import _pipeline_store, select_threat_technique_id
from app.features.alerts.generator import generate_alert
from app.features.validator.service import validate_playbook

logger = get_logger(__name__)

router = APIRouter(prefix="/pipeline", tags=["Pipeline SSE"])


def _sse_event(event_type: str, data: dict) -> str:
    """Format a Server-Sent Event string."""
    payload = json.dumps(data, default=str)
    return f"event: {event_type}\ndata: {payload}\n\n"


async def _stream_investigation(
    alert: AlertInput,
    include_threat_scenario: bool,
    threat_technique_id: str | None,
) -> AsyncGenerator[str, None]:
    """Run investigation pipeline with SSE streaming.

    Yields SSE events as each agent starts and completes.
    """
    investigation_id = f"INV-{uuid.uuid4().hex[:8].upper()}"
    pipeline_start = time.time()

    state = PipelineState(
        investigation_id=investigation_id,
        alert=alert,
        status=InvestigationStatus.PENDING,
    )

    if not alert.alert_id:
        alert.alert_id = f"ALERT-{uuid.uuid4().hex[:8].upper()}"

    yield _sse_event("pipeline_started", {
        "investigation_id": investigation_id,
        "alert_id": alert.alert_id,
        "severity": alert.severity.value,
        "rule_name": alert.rule_name,
        "total_agents": 9 if include_threat_scenario else 8,
    })

    async def _run_threat_scenario() -> dict:
        selected_technique = select_threat_technique_id(
            state.mitre_result or {},
            threat_technique_id,
        )
        if not selected_technique:
            return {"_agent": "Threat Generator", "confidence": None, "skipped": True}
        return await generate_threat_scenario(
            technique_id=selected_technique,
            apt_group="generic",
            additional_context={
                "source": "sse",
                "alert_id": alert.alert_id,
            },
        )

    agents = [
        {
            "step": "orchestrator",
            "name": "Orchestrator",
            "role": "SOC Manager",
            "model": "Qwen3-7B",
            "fn": lambda: route_alert(alert),
            "status": InvestigationStatus.TRIAGING,
        },
        {
            "step": "l1_triage",
            "name": "L1 Triage",
            "role": "L1 Analyst",
            "model": "Qwen3-4B",
            "fn": lambda: classify_alert(alert, orchestrator_context=state.orchestrator_result),
            "status": InvestigationStatus.TRIAGING,
        },
        {
            "step": "evidence_collector",
            "name": "Evidence Collector",
            "role": "L2 Analyst",
            "model": "Qwen3-7B",
            "fn": lambda: collect_evidence(alert, triage_context=state.triage_result),
            "status": InvestigationStatus.COLLECTING_EVIDENCE,
        },
        {
            "step": "mitre_mapper",
            "name": "MITRE Mapper",
            "role": "L2/L3 Analyst",
            "model": "Qwen3-7B",
            "fn": lambda: map_to_attack(alert, evidence_context=state.evidence_result),
            "status": InvestigationStatus.MAPPING_MITRE,
        },
    ]

    if include_threat_scenario:
        agents.append({
            "step": "threat_generator",
            "name": "Threat Generator",
            "role": "Threat Intelligence Analyst",
            "model": "Qwen3-7B",
            "fn": _run_threat_scenario,
            "status": InvestigationStatus.GENERATING_THREAT_SCENARIO,
        })

    agents.extend([
        {
            "step": "detection",
            "name": "Detection Agent",
            "role": "Detection Engineer",
            "model": "Qwen3-7B",
            "fn": lambda: generate_detection(
                alert_data=alert.model_dump(),
                mitre_result=state.mitre_result or {},
                evidence_result=state.evidence_result or {},
            ),
            "status": InvestigationStatus.GENERATING_DETECTION,
        },
        {
            "step": "report_writer",
            "name": "Report Writer",
            "role": "Senior Analyst",
            "model": "Qwen3-14B",
            "fn": lambda: generate_report(
                alert_data=alert.model_dump(),
                triage_result=state.triage_result or {},
                evidence_result=state.evidence_result or {},
                mitre_result=state.mitre_result or {},
                detection_result=state.detection_result or {},
            ),
            "status": InvestigationStatus.GENERATING_REPORT,
        },
        {
            "step": "response_planner",
            "name": "Response Planner",
            "role": "L3 Incident Responder",
            "model": "Qwen3-14B",
            "fn": lambda: generate_playbook(
                alert_data=alert.model_dump(),
                triage_result=state.triage_result or {},
                evidence_result=state.evidence_result or {},
                mitre_result=state.mitre_result or {},
                report_result=state.report_result or {},
            ),
            "status": InvestigationStatus.GENERATING_RESPONSE,
        },
        {
            "step": "validator",
            "name": "Adversarial Validator",
            "role": "Red Teamer / Critic",
            "model": "Qwen3-7B",
            "fn": lambda: validate_playbook(
                alert_data=alert.model_dump(),
                playbook_result=state.response_result or {},
            ),
            "status": InvestigationStatus.VALIDATING,
        },
    ])

    try:
        for i, agent in enumerate(agents):
            state.status = agent["status"]

            # Emit agent_started
            yield _sse_event("agent_started", {
                "investigation_id": investigation_id,
                "agent_index": i,
                "agent_name": agent["name"],
                "agent_role": agent["role"],
                "agent_model": agent["model"],
                "step": agent["step"],
            })

            # Small delay to allow SSE flush
            await asyncio.sleep(0.05)

            # Execute agent
            step_start = time.time()
            result = await agent["fn"]()
            step_time = round((time.time() - step_start) * 1000, 1)

            # Store result in state
            result_key = f"{agent['step'].replace('l1_', '')}_result"
            if agent["step"] == "orchestrator":
                state.orchestrator_result = result
            elif agent["step"] == "l1_triage":
                state.triage_result = result
            elif agent["step"] == "evidence_collector":
                state.evidence_result = result
            elif agent["step"] == "mitre_mapper":
                state.mitre_result = result
            elif agent["step"] == "threat_generator":
                state.threat_scenario = result
            elif agent["step"] == "detection":
                state.detection_result = result
            elif agent["step"] == "report_writer":
                state.report_result = result
            elif agent["step"] == "response_planner":
                state.response_result = result
            elif agent["step"] == "validator":
                state.validator_result = result

            # Add audit entry
            state.audit_trail.append({
                "timestamp": datetime.utcnow().isoformat(),
                "step": agent["step"],
                "agent": agent["name"],
                "processing_time_ms": step_time,
                "confidence": result.get("confidence", None),
                "status": "completed",
            })

            # Emit agent_completed
            yield _sse_event("agent_completed", {
                "investigation_id": investigation_id,
                "agent_index": i,
                "agent_name": agent["name"],
                "processing_time_ms": step_time,
                "confidence": result.get("confidence", None),
                "classification": result.get("classification", None),
                "status": "completed",
            })

            # Check for early exit (false positive)
            if agent["step"] == "l1_triage":
                classification = result.get("classification", "investigate")
                if classification == "close":
                    state.status = InvestigationStatus.COMPLETED
                    state.completed_at = datetime.utcnow().isoformat()
                    state.total_processing_time_ms = round(
                        (time.time() - pipeline_start) * 1000, 1
                    )
                    _pipeline_store[investigation_id] = state

                    yield _sse_event("pipeline_completed", {
                        "investigation_id": investigation_id,
                        "status": "completed",
                        "early_exit": True,
                        "reason": "false_positive",
                        "total_processing_time_ms": state.total_processing_time_ms,
                        "agents_completed": i + 1,
                    })
                    return

        # Pipeline complete
        state.status = InvestigationStatus.COMPLETED
        state.completed_at = datetime.utcnow().isoformat()
        state.total_processing_time_ms = round(
            (time.time() - pipeline_start) * 1000, 1
        )
        _pipeline_store[investigation_id] = state

        yield _sse_event("pipeline_completed", {
            "investigation_id": investigation_id,
            "status": "completed",
            "total_processing_time_ms": state.total_processing_time_ms,
            "agents_completed": len(agents),
        })

    except Exception as e:
        state.status = InvestigationStatus.FAILED
        state.completed_at = datetime.utcnow().isoformat()
        state.total_processing_time_ms = round(
            (time.time() - pipeline_start) * 1000, 1
        )
        _pipeline_store[investigation_id] = state

        yield _sse_event("pipeline_failed", {
            "investigation_id": investigation_id,
            "error": str(e),
            "total_processing_time_ms": state.total_processing_time_ms,
        })

        logger.error(
            "SSE pipeline failed",
            investigation_id=investigation_id,
            error=str(e),
        )


@router.get("/stream-investigate")
async def stream_investigate_endpoint(
    scenario: str = "brute_force",
    include_threat_scenario: bool = False,
    threat_technique_id: str | None = None,
):
    """Stream a demo investigation via Server-Sent Events.

    Generates a synthetic alert and streams real-time agent-by-agent
    progress as each agent starts and completes.

    Events emitted:
    - pipeline_started: Investigation begins
    - agent_started: Agent begins processing
    - agent_completed: Agent finished with result summary
    - pipeline_completed: All agents done
    - pipeline_failed: Error occurred
    """
    alert = generate_alert(scenario)

    return StreamingResponse(
        _stream_investigation(alert, include_threat_scenario, threat_technique_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/stream-investigate-alert")
async def stream_investigate_alert_endpoint(
    alert: AlertInput,
    include_threat_scenario: bool = False,
    threat_technique_id: str | None = None,
):
    """Stream an investigation on a specific alert via SSE."""
    return StreamingResponse(
        _stream_investigation(alert, include_threat_scenario, threat_technique_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
