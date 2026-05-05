"""
SOCsentinel — MITRE Mapper Agent service.

Maps observed attack behaviors to MITRE ATT&CK techniques
using RAG-grounded reasoning from the ChromaDB knowledge base.
"""

import json
from typing import Any

from app.core.logger import get_logger
from app.shared.agent_runner import run_agent
from app.shared.llm.client import get_mitre_llm
from app.shared.llm.prompt_manager import render_prompt
from app.shared.rag.retriever import retrieve_techniques, format_techniques_for_prompt
from app.shared.schemas import AlertInput

logger = get_logger(__name__)


async def map_to_attack(
    alert: AlertInput,
    evidence_context: dict | None = None,
) -> dict[str, Any]:
    """Map alert behaviors to MITRE ATT&CK techniques.

    Uses RAG to retrieve relevant techniques from the knowledge base,
    then passes them as context to the LLM for grounded mapping.

    Args:
        alert: Parsed SIEM alert input.
        evidence_context: Optional context from the Evidence Collector.

    Returns:
        MITRE mapping result with techniques, timeline, and kill chain phase.
    """
    llm = get_mitre_llm()

    # Build query from alert + evidence for RAG retrieval
    query_parts = [alert.description, alert.rule_name]
    if evidence_context:
        query_parts.append(evidence_context.get("enrichment_summary", ""))
        for ioc in evidence_context.get("iocs", []):
            query_parts.append(f"{ioc.get('type', '')}: {ioc.get('context', '')}")

    rag_query = " ".join(filter(None, query_parts))

    # Retrieve relevant MITRE techniques via RAG
    techniques = retrieve_techniques(rag_query, n_results=8)
    mitre_context = format_techniques_for_prompt(techniques)

    # Render system prompt with RAG context injected
    system_prompt = render_prompt("mitre_mapper_system", mitre_context=mitre_context)

    context_str = ""
    if evidence_context:
        context_str = (
            "\n\nEvidence Context:\n"
            f"{json.dumps(evidence_context, indent=2, default=str)}"
        )

    user_message = (
        "Map the following alert behaviors to MITRE ATT&CK techniques:\n\n"
        f"{json.dumps(alert.model_dump(), indent=2, default=str)}"
        f"{context_str}"
    )

    result = await run_agent(
        agent_name="MITRE Mapper",
        llm=llm,
        system_prompt=system_prompt,
        user_message=user_message,
    )

    if not result.get("alert_id"):
        result["alert_id"] = alert.alert_id

    return result
