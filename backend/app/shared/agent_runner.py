"""
SOCsentinel — Base agent runner.

Provides a reusable pattern for all agents: load prompt, invoke LLM,
parse JSON output, record audit trail entry.
"""

import json
import time
from typing import Any

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage

from app.core.logger import get_logger
from app.shared.llm.guardrails import validate_input, validate_output
from app.shared.exceptions.base import AgentError, LLMError

logger = get_logger(__name__)


async def run_agent(
    agent_name: str,
    llm: BaseChatModel,
    system_prompt: str,
    user_message: str,
) -> dict[str, Any]:
    """Run an agent with the given LLM and prompts.

    This is the unified execution pattern for all SOCsentinel agents.
    It handles input validation, LLM invocation, output parsing, and timing.

    Args:
        agent_name: Human-readable agent name for logging/audit.
        llm: The LLM client instance to use.
        system_prompt: The system prompt defining the agent's role.
        user_message: The user/task message with alert data.

    Returns:
        Parsed JSON dict from the agent's response.

    Raises:
        AgentError: If the agent fails to produce valid output.
        LLMError: If the LLM call itself fails.
    """
    # Validate input
    is_valid, msg = validate_input(user_message)
    if not is_valid:
        raise AgentError(agent_name, f"Input validation failed: {msg}")

    start_time = time.time()

    try:
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message),
        ]

        logger.info(
            "Agent invocation started",
            agent=agent_name,
            input_length=len(user_message),
        )

        response = await llm.ainvoke(messages)
        raw_output = response.content

    except Exception as e:
        elapsed = (time.time() - start_time) * 1000
        logger.error(
            "LLM invocation failed",
            agent=agent_name,
            error=str(e),
            elapsed_ms=round(elapsed, 1),
        )
        raise LLMError(f"Agent '{agent_name}' LLM call failed: {e}") from e

    elapsed_ms = (time.time() - start_time) * 1000

    # Validate output
    is_valid, sanitized = validate_output(raw_output)
    if not is_valid:
        raise AgentError(agent_name, f"Output validation failed: {sanitized}")

    # Parse JSON from response
    parsed = _extract_json(sanitized, agent_name)

    # Inject metadata
    parsed["_agent"] = agent_name
    parsed["_processing_time_ms"] = round(elapsed_ms, 1)

    logger.info(
        "Agent invocation completed",
        agent=agent_name,
        elapsed_ms=round(elapsed_ms, 1),
        confidence=parsed.get("confidence", "N/A"),
    )

    return parsed


def _extract_json(text: str, agent_name: str) -> dict[str, Any]:
    """Extract JSON from LLM response text.

    Handles cases where the LLM wraps JSON in markdown code blocks.

    Args:
        text: Raw LLM output text.
        agent_name: Agent name for error context.

    Returns:
        Parsed dict.

    Raises:
        AgentError: If JSON parsing fails.
    """
    cleaned = text.strip()

    # Strip markdown code block wrappers if present
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        # Remove first line (```json) and last line (```)
        lines = [l for l in lines if not l.strip().startswith("```")]
        cleaned = "\n".join(lines).strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Try to find JSON object within the text
        start = cleaned.find("{")
        end = cleaned.rfind("}") + 1
        if start >= 0 and end > start:
            try:
                return json.loads(cleaned[start:end])
            except json.JSONDecodeError:
                pass

        logger.error(
            "Failed to parse agent JSON output",
            agent=agent_name,
            output_preview=text[:200],
        )
        raise AgentError(
            agent_name,
            "Failed to parse JSON from agent response. Raw output: " + text[:200],
        )
