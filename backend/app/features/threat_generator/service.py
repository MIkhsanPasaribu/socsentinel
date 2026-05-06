"""
SOCsentinel — Threat Generator Agent service.

Generates realistic attack scenarios based on MITRE ATT&CK techniques.
Used for:
1. Proactive threat hunting
2. Detection validation (purple team exercises)
3. SOC analyst training
4. Simulating potential attack chains
"""

import json
from typing import Any

from app.core.config import get_settings
from app.core.logger import get_logger
from app.features.threat_intel.service import fetch_threat_intel
from app.shared.agent_runner import run_agent
from app.shared.llm.client import create_llm_client
from app.shared.llm.prompt_manager import load_prompt

logger = get_logger(__name__)


async def generate_threat_scenario(
    technique_id: str,
    apt_group: str = "generic",
    additional_context: dict[str, Any] | None = None,
    include_threat_intel: bool = False,
    intel_keywords: list[str] | None = None,
) -> dict[str, Any]:
    """Generate a threat scenario from a MITRE ATT&CK technique.

    Args:
        technique_id: MITRE ATT&CK technique ID (e.g., 'T1110').
        apt_group: Specific APT group to model after (optional).
        additional_context: Extra context for scenario generation (optional).

    Returns:
        Threat scenario with attack chain and simulation commands.
    """
    settings = get_settings()
    llm = create_llm_client(model_name=settings.qwen3_7b_model)
    system_prompt = load_prompt("threat_generator_system")

    threat_intel_summary: dict[str, Any] | None = None
    if include_threat_intel:
        if settings.taxii_server_url and settings.taxii_collection_id:
            try:
                threat_intel_summary = await fetch_threat_intel(
                    server_url=settings.taxii_server_url,
                    api_root=settings.taxii_api_root,
                    collection_id=settings.taxii_collection_id,
                    token=settings.taxii_token or None,
                )
            except Exception as exc:
                logger.warning(
                    "Threat intel enrichment failed",
                    error=str(exc),
                )
        else:
            logger.warning("Threat intel enrichment requested without TAXII config")

    intel_keywords = intel_keywords or []
    if threat_intel_summary and intel_keywords:
        keywords = [keyword.lower() for keyword in intel_keywords]
        indicators = threat_intel_summary.get("indicators", [])
        filtered = [
            indicator
            for indicator in indicators
            if any(keyword in str(indicator).lower() for keyword in keywords)
        ]
        threat_intel_summary["indicators"] = filtered

    context = {
        "technique_id": technique_id,
        "apt_group": apt_group,
        "additional_context": additional_context or {},
        "threat_intel": threat_intel_summary or {},
        "intel_keywords": intel_keywords,
    }

    user_message = (
        f"Generate a realistic threat scenario based on the following parameters:\n\n"
        f"{json.dumps(context, indent=2, default=str)}\n\n"
        "Create a detailed attack chain with realistic steps, expected telemetry, "
        "and simulation commands that can be used for purple team exercises."
    )

    result = await run_agent(
        agent_name="Threat Generator",
        llm=llm,
        system_prompt=system_prompt,
        user_message=user_message,
    )

    logger.info(
        "Threat scenario generated",
        scenario_name=result.get("scenario_name", "unknown"),
        technique_id=technique_id,
    )

    return result