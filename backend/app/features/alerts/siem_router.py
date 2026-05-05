"""
SOCsentinel — SIEM webhook router.

Receives alerts from external SIEM platforms via webhooks.
Currently supports:
- Wazuh (POST /api/v1/siem/wazuh/webhook)

Configure Wazuh integration:
  In ossec.conf → <integration>:
    <name>custom-socsentinel</name>
    <hook_url>http://socsentinel:8000/api/v1/siem/wazuh/webhook</hook_url>
    <level>5</level>
    <alert_format>json</alert_format>
  </integration>
"""

from fastapi import APIRouter, BackgroundTasks

from app.shared.schemas import APIResponse
from app.shared.siem.connector import get_connector
from app.features.pipeline.service import run_investigation
from app.core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/siem", tags=["SIEM Integration"])


@router.post("/wazuh/webhook", response_model=APIResponse)
async def wazuh_webhook(
    event: dict,
    background_tasks: BackgroundTasks,
    auto_investigate: bool = False,
) -> APIResponse:
    """Receive a Wazuh alert via webhook.

    Normalizes the Wazuh alert into SOCsentinel format.
    Optionally triggers auto-investigation via the 5-agent pipeline.

    Configure in Wazuh's ossec.conf integration block to send
    alerts above a threshold level.

    Args:
        event: Raw Wazuh alert JSON.
        auto_investigate: If True, auto-trigger investigation pipeline.
    """
    connector = get_connector("wazuh")
    alert = connector.normalize_alert(event)

    result = {
        "alert_id": alert.alert_id,
        "severity": alert.severity.value,
        "rule_name": alert.rule_name,
        "source_ip": alert.source_ip,
        "hostname": alert.hostname,
        "connector": "wazuh",
        "auto_investigate": auto_investigate,
    }

    if auto_investigate:
        # Run investigation asynchronously in the background
        background_tasks.add_task(run_investigation, alert)
        result["investigation_status"] = "queued"
        logger.info(
            "Wazuh alert queued for auto-investigation",
            alert_id=alert.alert_id,
        )
    else:
        result["investigation_status"] = "pending_manual"

    return APIResponse(
        success=True,
        message=f"Wazuh alert received: {alert.alert_id}",
        data=result,
    )


@router.post("/ingest", response_model=APIResponse)
async def generic_ingest(
    event: dict,
    connector_name: str = "synthetic",
    auto_investigate: bool = False,
    background_tasks: BackgroundTasks = None,
) -> APIResponse:
    """Generic SIEM alert ingestion endpoint.

    Accepts alerts from any supported SIEM connector.

    Args:
        event: Raw alert event dict.
        connector_name: SIEM connector to use ('wazuh', 'synthetic').
        auto_investigate: If True, auto-trigger investigation pipeline.
    """
    connector = get_connector(connector_name)
    alert = connector.normalize_alert(event)

    result = {
        "alert_id": alert.alert_id,
        "severity": alert.severity.value,
        "connector": connector_name,
    }

    if auto_investigate and background_tasks:
        background_tasks.add_task(run_investigation, alert)
        result["investigation_status"] = "queued"

    return APIResponse(
        success=True,
        message=f"Alert ingested via {connector_name}: {alert.alert_id}",
        data=result,
    )
