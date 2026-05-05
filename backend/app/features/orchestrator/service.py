"""
SOCsentinel — Orchestrator Agent service.

Parses raw SIEM alerts, assigns priority, and routes to the
appropriate downstream agent.
"""

import json
from typing import Any

from app.core.logger import get_logger
from app.shared.agent_runner import run_agent
from app.shared.llm.client import get_orchestrator_llm
from app.shared.llm.prompt_manager import load_prompt
from app.shared.schemas import AlertInput

logger = get_logger(__name__)


async def route_alert(alert: AlertInput) -> dict[str, Any]:
    """Route an incoming alert through the Orchestrator agent.

    Args:
        alert: Parsed SIEM alert input.

    Returns:
        Orchestrator routing decision dict.
    """
    llm = get_orchestrator_llm()
    system_prompt = load_prompt("orchestrator_system")

    user_message = (
        "Analyze the following SIEM alert and decide how to route it:\n\n"
        f"{json.dumps(alert.model_dump(), indent=2, default=str)}"
    )

    result = await run_agent(
        agent_name="Orchestrator",
        llm=llm,
        system_prompt=system_prompt,
        user_message=user_message,
    )

    # Ensure alert_id is set
    if not result.get("alert_id"):
        result["alert_id"] = alert.alert_id

    return result
