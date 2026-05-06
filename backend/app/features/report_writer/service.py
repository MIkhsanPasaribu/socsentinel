"""
SOCsentinel — Report Writer Agent service.

Synthesizes all agent outputs into a comprehensive
investigation report with recommendations.
"""

import json
from typing import Any

from app.core.logger import get_logger
from app.shared.agent_runner import run_agent
from app.shared.llm.client import get_report_llm
from app.shared.llm.prompt_manager import load_prompt

logger = get_logger(__name__)


async def generate_report(
    alert_data: dict,
    triage_result: dict | None = None,
    evidence_result: dict | None = None,
    mitre_result: dict | None = None,
    detection_result: dict | None = None,
) -> dict[str, Any]:
    """Generate an investigation report from all agent outputs.

    Args:
        alert_data: Original alert data dict.
        triage_result: Output from L1 Triage agent.
        evidence_result: Output from Evidence Collector agent.
        mitre_result: Output from MITRE Mapper agent.
        detection_result: Output from Detection agent (Sigma rules).

    Returns:
        Structured investigation report dict.
    """
    llm = get_report_llm()
    system_prompt = load_prompt("report_writer_system")

    # Compile all context
    context = {
        "original_alert": alert_data,
        "triage_analysis": triage_result or {},
        "evidence_collection": evidence_result or {},
        "mitre_mapping": mitre_result or {},
        "detection_rules": detection_result or {},
    }

    user_message = (
        "Generate a comprehensive investigation report based on all agent findings below.\n"
        "Synthesize the data into a coherent narrative with actionable recommendations.\n\n"
        f"{json.dumps(context, indent=2, default=str)}"
    )

    result = await run_agent(
        agent_name="Report Writer",
        llm=llm,
        system_prompt=system_prompt,
        user_message=user_message,
    )

    if not result.get("alert_id"):
        result["alert_id"] = alert_data.get("alert_id", "")

    return result
