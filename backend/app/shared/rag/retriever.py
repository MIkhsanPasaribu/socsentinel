"""
SOCsentinel — MITRE ATT&CK retriever.

Queries the ChromaDB vector store to find relevant ATT&CK
techniques for grounding agent reasoning.
"""

from typing import Any

from app.core.logger import get_logger
from app.shared.rag.vector_store import query_documents

logger = get_logger(__name__)


def retrieve_techniques(
    query: str,
    n_results: int = 5,
    tactic_filter: str | None = None,
) -> list[dict[str, Any]]:
    """Retrieve relevant MITRE ATT&CK techniques for a given query.

    Args:
        query: Natural language description of observed behavior.
        n_results: Maximum number of techniques to return.
        tactic_filter: Optional filter by tactic name.

    Returns:
        List of technique dicts with 'technique_id', 'name', 'tactic',
        'description', 'relevance_score'.
    """
    where = None
    if tactic_filter:
        where = {"tactic": tactic_filter}

    # Handle empty collection gracefully
    from app.shared.rag.vector_store import get_collection
    collection = get_collection()
    if collection.count() == 0:
        logger.info("MITRE ATT&CK collection is empty, skipping RAG retrieval")
        return []

    results = query_documents(query_text=query, n_results=n_results, where=where)

    techniques = []
    if results and results.get("ids") and results["ids"][0]:
        for i, doc_id in enumerate(results["ids"][0]):
            metadata = results["metadatas"][0][i] if results.get("metadatas") else {}
            document = results["documents"][0][i] if results.get("documents") else ""
            distance = results["distances"][0][i] if results.get("distances") else 1.0

            # Convert distance to relevance score (lower distance = higher relevance)
            relevance_score = max(0.0, 1.0 - (distance / 2.0))

            techniques.append({
                "technique_id": metadata.get("technique_id", doc_id),
                "name": metadata.get("name", "Unknown"),
                "tactic": metadata.get("tactic", "Unknown"),
                "description": document[:500],
                "relevance_score": round(relevance_score, 3),
                "platform": metadata.get("platform", ""),
                "url": metadata.get("url", ""),
            })

    logger.info(
        "MITRE techniques retrieved",
        query_preview=query[:80],
        count=len(techniques),
    )
    return techniques


def format_techniques_for_prompt(techniques: list[dict[str, Any]]) -> str:
    """Format retrieved techniques as context string for LLM prompts.

    Args:
        techniques: List of technique dicts from retrieve_techniques().

    Returns:
        Formatted string suitable for LLM context injection.
    """
    if not techniques:
        return "No matching MITRE ATT&CK techniques found."

    lines = ["Relevant MITRE ATT&CK Techniques:"]
    for i, tech in enumerate(techniques, 1):
        lines.append(
            f"\n[{i}] {tech['technique_id']} — {tech['name']}"
            f"\n    Tactic: {tech['tactic']}"
            f"\n    Relevance: {tech['relevance_score']:.0%}"
            f"\n    Description: {tech['description'][:200]}..."
        )
    return "\n".join(lines)
