"""
SOCsentinel — Response Planner Agent service.

6th agent in the pipeline. Generates automated containment playbooks
with prioritized response steps based on the full investigation output.

Maps to the detect → investigate → RESPOND workflow completion.
"""

from typing import Any

from app.core.config import get_settings
from app.core.logger import get_logger
from app.shared.agent_runner import run_agent
from app.shared.llm.client import create_llm_client
from app.shared.llm.prompt_manager import load_prompt

logger = get_logger(__name__)

async def generate_playbook(
    alert_data: dict[str, Any],
    triage_result: dict[str, Any],
    evidence_result: dict[str, Any],
    mitre_result: dict[str, Any],
    report_result: dict[str, Any],
) -> dict[str, Any]:
    """Generate a response playbook from investigation outputs.

    Args:
        alert_data: Original alert data.
        triage_result: L1 triage classification result.
        evidence_result: Evidence collector IOC/enrichment result.
        mitre_result: MITRE ATT&CK mapping result.
        report_result: Report writer output.

    Returns:
        Response playbook with containment steps.
    """
    settings = get_settings()
    llm = create_llm_client(model_name=settings.qwen3_14b_model)
    system_prompt = load_prompt("response_planner_system")

    user_message = (
        "Generate a containment and response playbook for this investigation.\n\n"
        f"Alert Data:\n{alert_data}\n\n"
        f"Triage Result:\n{triage_result}\n\n"
        f"Evidence (IOCs):\n{evidence_result}\n\n"
        f"MITRE ATT&CK Mapping:\n{mitre_result}\n\n"
        f"Investigation Report:\n{report_result}"
    )

    result = await run_agent(
        agent_name="Response Planner",
        llm=llm,
        system_prompt=system_prompt,
        user_message=user_message,
    )

    logger.info(
        "Response playbook generated",
        playbook_name=result.get("playbook_name", ""),
        steps=len(result.get("steps", [])),
    )

    return result
