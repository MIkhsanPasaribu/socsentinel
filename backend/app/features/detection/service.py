"""
SOCsentinel — Detection Agent service.

Generates deployable Sigma rules from MITRE ATT&CK mappings
and investigation findings. This is the core detection engineering
agent that transforms threat intelligence into actionable
detection logic.
"""

import json
from typing import Any

from app.core.logger import get_logger
from app.shared.agent_runner import run_agent
from app.shared.llm.client import create_llm_client
from app.shared.llm.prompt_manager import load_prompt
from app.core.config import get_settings

logger = get_logger(__name__)


async def generate_detection(
    alert_data: dict[str, Any],
    mitre_result: dict[str, Any],
    evidence_result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Generate a Sigma detection rule from investigation findings.

    Args:
        alert_data: Original alert data.
        mitre_result: MITRE ATT&CK mapping result with techniques.
        evidence_result: Evidence collector result with IOCs (optional).

    Returns:
        Detection rule with Sigma YAML and metadata.
    """
    settings = get_settings()
    llm = create_llm_client(model_name=settings.qwen3_7b_model)
    system_prompt = load_prompt("detection_system")

    techniques = mitre_result.get("techniques", [])
    iocs = evidence_result.get("iocs", []) if evidence_result else []

    user_message = _build_detection_prompt(alert_data, techniques, iocs, mitre_result)

    result = await run_agent(
        agent_name="Detection",
        llm=llm,
        system_prompt=system_prompt,
        user_message=user_message,
    )

    logger.info(
        "Detection rule generated",
        alert_id=alert_data.get("alert_id", "unknown"),
        has_sigma_rule=bool(result.get("sigma_rule")),
    )

    return result


def _build_detection_prompt(
    alert_data: dict[str, Any],
    techniques: list[dict],
    iocs: list[dict],
    mitre_result: dict[str, Any],
) -> str:
    """Build the user prompt for detection rule generation.

    Args:
        alert_data: Original alert.
        techniques: MITRE techniques list.
        iocs: IOC list from evidence collector.
        mitre_result: Full MITRE mapping result.

    Returns:
        Formatted user message for the LLM.
    """
    context = {
        "alert": alert_data,
        "mitre_techniques": techniques,
        "iocs": iocs,
        "kill_chain_phase": mitre_result.get("kill_chain_phase", ""),
        "attack_summary": mitre_result.get("attack_pattern_summary", ""),
    }

    return (
        "Generate a deployable Sigma detection rule from the investigation findings below.\n\n"
        "The Sigma rule must be valid YAML and map to the correct MITRE ATT&CK techniques.\n"
        "Include proper logsource context and detection conditions.\n\n"
        f"{json.dumps(context, indent=2, default=str)}\n\n"
        "Generate the detection rule following Sigma specification."
    )