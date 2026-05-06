"""
SOCsentinel — SOAR integration service.
"""

from typing import Any

from app.core.logger import get_logger
from app.shared.exceptions.base import ValidationError, NotFoundError
from app.features.pipeline.service import get_investigation

logger = get_logger(__name__)


def export_to_soar(
    platform: str,
    investigation_id: str,
    payload: dict[str, Any] | None,
) -> dict[str, Any]:
    """Export investigation results to SOAR-specific formats.

    Args:
        platform: Target SOAR platform.
        investigation_id: Investigation identifier.
        payload: Investigation data.

    Returns:
        SOAR-specific payload.
    """
    exporters = {
        "splunk": _export_splunk_soar,
        "xsoar": _export_xsoar,
        "sentinel": _export_sentinel,
        "generic": _export_generic,
    }
    normalized_platform = platform.lower().strip()
    exporter = exporters.get(normalized_platform)
    if not exporter:
        raise ValidationError(
            message="Unsupported SOAR platform",
            details={"platform": platform, "supported": list(exporters.keys())},
        )

    export_payload = payload
    if export_payload is None:
        state = get_investigation(investigation_id)
        if not state:
            raise NotFoundError("Investigation", investigation_id)
        export_payload = state.model_dump()

    result = exporter(investigation_id, export_payload)
    logger.info(
        "SOAR export generated",
        platform=normalized_platform,
        investigation_id=investigation_id,
    )
    return result


def _export_splunk_soar(investigation_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Map investigation payload to Splunk SOAR container schema."""
    return {
        "container": {
            "name": f"SOCsentinel Investigation {investigation_id}",
            "label": "event",
            "severity": payload.get("alert", {}).get("severity", "medium"),
            "source_data_identifier": investigation_id,
            "data": payload,
        },
        "artifacts": payload.get("evidence_result", {}).get("iocs", []),
    }


def _export_xsoar(investigation_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Map investigation payload to Cortex XSOAR incident schema."""
    return {
        "incident": {
            "name": f"SOCsentinel Investigation {investigation_id}",
            "type": "SOCsentinel",
            "severity": payload.get("alert", {}).get("severity", "medium"),
            "details": payload,
        }
    }


def _export_sentinel(investigation_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Map investigation payload to Microsoft Sentinel alert schema."""
    return {
        "alert": {
            "title": f"SOCsentinel Investigation {investigation_id}",
            "severity": payload.get("alert", {}).get("severity", "medium"),
            "description": payload.get("report_result", {}).get("executive_summary", ""),
            "entities": payload.get("evidence_result", {}).get("iocs", []),
        }
    }


def _export_generic(investigation_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Return a generic export payload for custom integrations."""
    return {
        "investigation_id": investigation_id,
        "payload": payload,
    }
