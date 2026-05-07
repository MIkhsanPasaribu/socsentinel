"""
SOCsentinel — L1 Triage Agent service.

Classifies alerts as investigate/close/escalate with severity scoring
and false positive detection.
"""

import json
from typing import Any

from app.core.logger import get_logger
from app.shared.agent_runner import run_agent
from app.shared.llm.client import get_triage_llm
from app.shared.llm.prompt_manager import load_prompt
from app.shared.schemas import AlertInput
from app.features.pipeline.feedback import get_relevant_feedback

logger = get_logger(__name__)


async def classify_alert(alert: AlertInput, orchestrator_context: dict | None = None) -> dict[str, Any]:
    """Classify an alert through the L1 Triage agent.

    Args:
        alert: Parsed SIEM alert input.
        orchestrator_context: Optional context from the Orchestrator.

    Returns:
        Triage classification result dict.
    """
    llm = get_triage_llm()
    system_prompt = load_prompt("triage_system")

    context_str = ""
    if orchestrator_context:
        context_str = (
            "\n\nOrchestrator Context:\n"
            f"{json.dumps(orchestrator_context, indent=2, default=str)}"
        )

    # Self-improving feedback loop: inject historical analyst decisions
    feedback = get_relevant_feedback(alert.rule_name)
    if feedback:
        context_str += (
            "\n\nHistorical Analyst Feedback for similar alerts:\n"
            f"{json.dumps(feedback, indent=2, default=str)}\n"
            "Use this feedback to calibrate your classification. "
            "If analysts previously rejected or escalated similar alerts, "
            "adjust your confidence and classification accordingly."
        )

    user_message = (
        "Classify the following alert. Determine if it should be investigated, "
        "closed as false positive, or escalated:\n\n"
        f"{json.dumps(alert.model_dump(), indent=2, default=str)}"
        f"{context_str}"
    )

    result = await run_agent(
        agent_name="L1 Triage",
        llm=llm,
        system_prompt=system_prompt,
        user_message=user_message,
    )

    if not result.get("alert_id"):
        result["alert_id"] = alert.alert_id

    return result
