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
from app.features.pipeline.service import _pipeline_store, _persist_state, select_threat_technique_id
from app.features.pipeline.thinking import get_thinking_mode
from app.features.alerts.generator import generate_alert
from app.features.validator.service import validate_playbook

logger = get_logger(__name__)

router = APIRouter(prefix="/pipeline", tags=["Pipeline SSE"])


def _sse_event(event_type: str, data: dict) -> str:
    """Format a Server-Sent Event string."""
    payload = json.dumps(data, default=str)
    return f"event: {event_type}\ndata: {payload}\n\n"


def _get_thinking_content(step: str, result: dict) -> str:
    """Return simulated chain-of-thought reasoning for a given agent step.

    In production with vLLM, this would come from Qwen3's <think> blocks.
    In mock mode, we generate realistic reasoning text.
    """
    thinking_map = {
        "orchestrator": (
            "<think>\nAnalyzing incoming alert metadata...\n"
            "- Source IP reputation check: flagged in 3 threat feeds\n"
            "- Alert severity vs baseline: elevated, above normal threshold\n"
            "- Similar alerts in past 24h: 2 related events found\n"
            "- Routing decision: assign to full investigation pipeline\n"
            "- Priority: HIGH — multiple correlated indicators\n"
            "Conclusion: This alert requires full multi-agent investigation.\n</think>"
        ),
        "l1_triage": (
            "<think>\nPerforming initial triage classification...\n"
            f"- Classification result: {result.get('classification', 'investigate')}\n"
            f"- Confidence: {result.get('confidence', 'N/A')}\n"
            "- Checking for known false positive patterns: no match\n"
            "- Evaluating alert fidelity: high signal-to-noise ratio\n"
            "- Cross-referencing with recent similar alerts\n"
            "Decision: Proceed with deep investigation — indicators suggest genuine threat.\n</think>"
        ),
        "evidence_collector": (
            "<think>\nCollecting and correlating evidence...\n"
            "- Enriching IOCs from threat intelligence feeds\n"
            "- Cross-referencing source IP with Shodan, VirusTotal, AbuseIPDB\n"
            "- Checking for lateral movement indicators in log data\n"
            "- CVE correlation: checking if targeted services have known vulns\n"
            "- Building evidence chain for analyst review\n"
            "Evidence collection complete — sufficient data for MITRE mapping.\n</think>"
        ),
        "mitre_mapper": (
            "<think>\nMapping to MITRE ATT&CK framework...\n"
            "- Querying ChromaDB RAG for technique similarity\n"
            "- Top technique matches identified via semantic search\n"
            "- Evaluating kill chain phase from evidence patterns\n"
            "- Cross-referencing with known APT group TTPs\n"
            "- Confidence in mapping: high — multiple evidence points align\n"
            "MITRE mapping complete with RAG-grounded technique assignments.\n</think>"
        ),
        "threat_generator": (
            "<think>\nGenerating threat scenario for hunting...\n"
            "- Analyzing mapped techniques for attack progression\n"
            "- Modeling potential lateral movement paths\n"
            "- Generating indicators for proactive hunting\n"
            "Threat scenario generated for purple team exercises.\n</think>"
        ),
        "detection": (
            "<think>\nGenerating Sigma detection rule...\n"
            "- Analyzing log source requirements\n"
            "- Building detection logic from observed patterns\n"
            "- Evaluating false positive risk of rule\n"
            "- Mapping rule to MITRE techniques for coverage tracking\n"
            "- Optimizing rule specificity vs sensitivity balance\n"
            "Sigma rule generated — ready for SIEM deployment.\n</think>"
        ),
        "report_writer": (
            "<think>\nCompiling comprehensive investigation report...\n"
            "- Synthesizing findings from all previous agents\n"
            "- Writing executive summary for leadership\n"
            "- Documenting evidence chain with timestamps\n"
            "- Formulating actionable recommendations\n"
            "- Assessing overall threat impact and risk\n"
            "Report complete with executive summary and technical details.\n</think>"
        ),
        "response_planner": (
            "<think>\nDesigning containment and response playbook...\n"
            "- Evaluating containment options by risk level\n"
            "- Prioritizing actions: immediate isolation vs monitoring\n"
            "- Identifying automated vs manual response steps\n"
            "- Assessing blast radius of proposed actions\n"
            "- Building rollback procedures for each step\n"
            "Response playbook ready for analyst approval.\n</think>"
        ),
        "validator": (
            "<think>\nPerforming adversarial validation of response plan...\n"
            "- Red team perspective: could the playbook be evaded?\n"
            "- Checking for collateral damage in proposed actions\n"
            "- Validating Sigma rule accuracy and coverage\n"
            "- Risk scoring each response step\n"
            "- Identifying safer alternatives where applicable\n"
            "Validation complete — playbook assessed with risk annotations.\n</think>"
        ),
    }
    return thinking_map.get(step, "<think>\nProcessing...\nAnalysis complete.\n</think>")


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

    thinking_mode = get_thinking_mode()

    yield _sse_event("pipeline_started", {
        "investigation_id": investigation_id,
        "alert_id": alert.alert_id,
        "severity": alert.severity.value,
        "rule_name": alert.rule_name,
        "total_agents": 9,
        "thinking_mode": thinking_mode,
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
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "step": agent["step"],
                "agent": agent["name"],
                "processing_time_ms": step_time,
                "confidence": result.get("confidence", None),
                "status": "completed",
            })

            # Build agent_completed event
            completed_event: dict = {
                "investigation_id": investigation_id,
                "agent_index": i,
                "agent_name": agent["name"],
                "processing_time_ms": step_time,
                "confidence": result.get("confidence", None),
                "classification": result.get("classification", None),
                "status": "completed",
            }

            # Include thinking content when thinking mode is enabled
            if thinking_mode:
                completed_event["thinking_content"] = _get_thinking_content(
                    agent["step"], result
                )

            yield _sse_event("agent_completed", completed_event)

            # Check for early exit (false positive)
            if agent["step"] == "l1_triage":
                classification = result.get("classification", "investigate")
                if classification == "close":
                    state.status = InvestigationStatus.COMPLETED
                    state.completed_at = datetime.utcnow().isoformat() + "Z"
                    state.total_processing_time_ms = round(
                        (time.time() - pipeline_start) * 1000, 1
                    )
                    _pipeline_store[investigation_id] = state
                    _persist_state(state)

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
        state.completed_at = datetime.utcnow().isoformat() + "Z"
        state.total_processing_time_ms = round(
            (time.time() - pipeline_start) * 1000, 1
        )
        _pipeline_store[investigation_id] = state
        _persist_state(state)

        yield _sse_event("pipeline_completed", {
            "investigation_id": investigation_id,
            "status": "completed",
            "total_processing_time_ms": state.total_processing_time_ms,
            "agents_completed": len(agents),
        })

    except Exception as e:
        state.status = InvestigationStatus.FAILED
        state.completed_at = datetime.utcnow().isoformat() + "Z"
        state.total_processing_time_ms = round(
            (time.time() - pipeline_start) * 1000, 1
        )
        _pipeline_store[investigation_id] = state
        _persist_state(state)

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
