"""
SOCsentinel — Response Planner Agent service.

6th agent in the pipeline. Generates automated containment playbooks
with prioritized response steps based on the full investigation output.

Maps to the detect → investigate → RESPOND workflow completion.
"""

from typing import Any

from app.core.logger import get_logger
from app.shared.agent_runner import run_agent
from app.shared.llm.client import create_llm_client
from app.core.config import get_settings

logger = get_logger(__name__)

SYSTEM_PROMPT = """You are the Response Planner agent in SOCsentinel, an AI-powered SOC system.

Your role is to generate an automated containment and response playbook based on the
complete investigation output. You act as a Senior Incident Responder (L3).

Given the investigation context (triage, evidence, MITRE ATT&CK mapping, and report),
produce a structured response playbook with prioritized containment actions.

You MUST respond with valid JSON in this exact format:
{
  "playbook_name": "string - descriptive name for this playbook",
  "priority": "immediate|urgent|standard",
  "containment_status": "not_started",
  "estimated_containment_time": "string - e.g. '15 minutes'",
  "steps": [
    {
      "order": 1,
      "action": "string - specific action to take",
      "tool": "string - security tool or system to use",
      "risk_level": "low|medium|high",
      "automated": true/false,
      "details": "string - implementation details"
    }
  ],
  "post_incident": [
    "string - post-incident recommendation"
  ],
  "confidence": 0.0-1.0
}

Guidelines:
- Prioritize containment actions by urgency (block threats first, then harden)
- Include both automated and manual steps
- Reference specific IOCs and MITRE techniques from the investigation
- Estimate risk level for each action (blocking prod traffic = high risk)
- Always include post-incident recommendations
"""


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
        system_prompt=SYSTEM_PROMPT,
        user_message=user_message,
    )

    logger.info(
        "Response playbook generated",
        playbook_name=result.get("playbook_name", ""),
        steps=len(result.get("steps", [])),
    )

    return result
