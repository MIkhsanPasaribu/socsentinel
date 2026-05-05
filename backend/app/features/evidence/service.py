"""
SOCsentinel — Evidence Collector Agent service.

Gathers IOCs, queries threat intelligence, looks up CVEs,
and builds comprehensive threat context.
"""

import json
from typing import Any

from app.core.logger import get_logger
from app.shared.agent_runner import run_agent
from app.shared.llm.client import get_evidence_llm
from app.shared.llm.prompt_manager import load_prompt
from app.shared.schemas import AlertInput

logger = get_logger(__name__)


async def collect_evidence(
    alert: AlertInput,
    triage_context: dict | None = None,
) -> dict[str, Any]:
    """Collect and enrich evidence for an alert.

    Args:
        alert: Parsed SIEM alert input.
        triage_context: Optional context from the L1 Triage agent.

    Returns:
        Evidence collection result dict with IOCs and enrichment.
    """
    llm = get_evidence_llm()
    system_prompt = load_prompt("evidence_system")

    context_str = ""
    if triage_context:
        context_str = (
            "\n\nTriage Context:\n"
            f"{json.dumps(triage_context, indent=2, default=str)}"
        )

    user_message = (
        "Collect evidence and enrich IOCs for the following alert:\n\n"
        f"{json.dumps(alert.model_dump(), indent=2, default=str)}"
        f"{context_str}"
    )

    result = await run_agent(
        agent_name="Evidence Collector",
        llm=llm,
        system_prompt=system_prompt,
        user_message=user_message,
    )

    if not result.get("alert_id"):
        result["alert_id"] = alert.alert_id

    return result
