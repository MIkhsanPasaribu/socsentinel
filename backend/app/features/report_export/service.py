"""
SOCsentinel — Report Export service.

Orchestrates PDF and DOCX generation from investigation pipeline state.
"""

from datetime import datetime
from io import BytesIO
from typing import Any

from app.core.logger import get_logger
from app.shared.schemas import PipelineState
from app.features.pipeline.service import get_investigation

logger = get_logger(__name__)


def build_report_context(state: PipelineState) -> dict[str, Any]:
    """Transform PipelineState into a structured report context.

    Normalizes all agent outputs into a consistent format
    suitable for template rendering.

    Args:
        state: The complete pipeline state with all agent results.

    Returns:
        Dictionary with normalized report context.
    """
    alert = state.alert

    # Normalize triage result
    triage = state.triage_result or {}
    triage_normalized = {
        "classification": triage.get("classification", "unknown"),
        "severity": triage.get("severity", alert.severity.value),
        "confidence": triage.get("confidence", 0.0),
        "is_false_positive": triage.get("is_false_positive", False),
        "false_positive_probability": triage.get("false_positive_probability", 0.0),
        "reasoning": triage.get("reasoning", ""),
        "evidence_chain": triage.get("evidence_chain", []),
    }

    # Normalize evidence result
    evidence = state.evidence_result or {}
    evidence_normalized = {
        "iocs": evidence.get("iocs", []),
        "cve_matches": evidence.get("cve_matches", []),
        "enrichment_summary": evidence.get("enrichment_summary", ""),
        "confidence": evidence.get("confidence", 0.0),
    }

    # Normalize MITRE result
    mitre = state.mitre_result or {}
    techniques = mitre.get("techniques", [])
    normalized_techniques = []
    for t in techniques:
        normalized_techniques.append({
            "technique_id": t.get("technique_id") or t.get("id", ""),
            "technique_name": t.get("technique_name") or t.get("name", ""),
            "tactic": t.get("tactic", ""),
            "confidence": t.get("confidence", 0.0),
            "evidence": t.get("evidence", ""),
        })

    mitre_normalized = {
        "techniques": normalized_techniques,
        "attack_timeline": mitre.get("attack_timeline", []),
        "kill_chain_phase": mitre.get("kill_chain_phase", ""),
        "confidence": mitre.get("confidence", 0.0),
    }

    # Normalize detection result
    detection = state.detection_result or {}
    detection_normalized = {
        "sigma_rule": detection.get("sigma_rule", ""),
        "mitre_techniques_mapped": detection.get("mitre_techniques_mapped", []),
        "detection_logic": detection.get("detection_logic", ""),
        "confidence": detection.get("confidence", 0.0),
        "false_positive_risk": detection.get("false_positive_risk", "unknown"),
        "recommended_log_sources": detection.get("recommended_log_sources", []),
    }

    # Normalize report result
    report = state.report_result or {}
    report_normalized = {
        "title": report.get("title", f"Investigation Report: {alert.rule_name}"),
        "executive_summary": report.get("executive_summary", ""),
        "severity": report.get("severity", alert.severity.value),
        "status": report.get("status", "unknown"),
        "recommendations": report.get("recommendations", []),
        "confidence": report.get("confidence", 0.0),
    }

    # Normalize response result
    response = state.response_result or {}
    response_normalized = {
        "playbook_name": response.get("playbook_name", ""),
        "priority": response.get("priority", "standard"),
        "containment_status": response.get("containment_status", "not_started"),
        "estimated_containment_time": response.get("estimated_containment_time", ""),
        "steps": response.get("steps", []),
        "post_incident": response.get("post_incident", []),
        "confidence": response.get("confidence", 0.0),
    }

    # Normalize validator result
    validator = state.validator_result or {}
    validator_normalized = {
        "is_approved": validator.get("is_approved", False),
        "risk_score": validator.get("risk_score", 1.0),
        "critic_comments": validator.get("critic_comments", ""),
        "safe_alternatives": validator.get("safe_alternatives", []),
        "sigma_rule": validator.get("sigma_rule", ""),
    }

    # Calculate overall confidence
    confidences = [
        triage_normalized["confidence"],
        evidence_normalized["confidence"],
        mitre_normalized["confidence"],
        detection_normalized["confidence"],
        report_normalized["confidence"],
        response_normalized["confidence"],
    ]
    overall_confidence = sum(confidences) / len(confidences) if confidences else 0.0

    # Build audit trail summary
    audit_summary = []
    for entry in state.audit_trail:
        audit_summary.append({
            "timestamp": entry.get("timestamp", ""),
            "step": entry.get("step", ""),
            "agent": entry.get("agent", ""),
            "status": entry.get("status", ""),
            "processing_time_ms": entry.get("processing_time_ms", 0),
        })

    return {
        "investigation_id": state.investigation_id,
        "generated_at": datetime.utcnow().isoformat(),
        "generated_at_formatted": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
        "alert": {
            "alert_id": alert.alert_id,
            "rule_name": alert.rule_name,
            "severity": alert.severity.value,
            "description": alert.description,
            "source_ip": alert.source_ip,
            "destination_ip": alert.destination_ip,
            "source_port": alert.source_port,
            "destination_port": alert.destination_port,
            "protocol": alert.protocol,
            "username": alert.username,
            "hostname": alert.hostname,
            "timestamp": alert.timestamp,
            "source": alert.source,
        },
        "triage": triage_normalized,
        "evidence": evidence_normalized,
        "mitre": mitre_normalized,
        "detection": detection_normalized,
        "report": report_normalized,
        "response": response_normalized,
        "validator": validator_normalized,
        "audit_trail": audit_summary,
        "total_processing_time_ms": state.total_processing_time_ms,
        "overall_confidence": round(overall_confidence, 2),
        "escalation": state.escalation_result or {},
        "analyst_decision": state.analyst_decision or {},
    }


async def export_investigation_pdf(investigation_id: str) -> BytesIO:
    """Generate a PDF report for an investigation.

    Args:
        investigation_id: The unique investigation ID.

    Returns:
        BytesIO buffer containing the PDF.

    Raises:
        ValueError: If investigation not found.
    """
    from .pdf_generator import generate_pdf

    state = get_investigation(investigation_id)
    if not state:
        raise ValueError(f"Investigation not found: {investigation_id}")

    context = build_report_context(state)
    pdf_buffer = generate_pdf(context)

    logger.info(
        "PDF report generated",
        investigation_id=investigation_id,
        size_bytes=pdf_buffer.getbuffer().nbytes,
    )

    return pdf_buffer


async def export_investigation_docx(investigation_id: str) -> BytesIO:
    """Generate a DOCX report for an investigation.

    Args:
        investigation_id: The unique investigation ID.

    Returns:
        BytesIO buffer containing the DOCX.

    Raises:
        ValueError: If investigation not found.
    """
    from .docx_generator import generate_docx

    state = get_investigation(investigation_id)
    if not state:
        raise ValueError(f"Investigation not found: {investigation_id}")

    context = build_report_context(state)
    docx_buffer = generate_docx(context)

    logger.info(
        "DOCX report generated",
        investigation_id=investigation_id,
        size_bytes=docx_buffer.getbuffer().nbytes,
    )

    return docx_buffer
