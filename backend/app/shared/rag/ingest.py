"""
SOCsentinel — MITRE ATT&CK data ingestion script.

Downloads and ingests the MITRE ATT&CK Enterprise Matrix
into ChromaDB for RAG-grounded reasoning.

Usage:
    python -m app.shared.rag.ingest
"""

import json
from pathlib import Path

import httpx

from app.core.logger import get_logger, setup_logging
from app.shared.rag.vector_store import add_documents, get_collection, reset_collection

logger = get_logger(__name__)

ATTACK_URL = "https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json"
DATA_DIR = Path(__file__).parent.parent.parent.parent.parent / "data" / "mitre_attack"


def download_attack_data(force: bool = False) -> Path:
    """Download MITRE ATT&CK Enterprise data if not cached.

    Args:
        force: Force re-download even if cached.

    Returns:
        Path to the downloaded JSON file.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    filepath = DATA_DIR / "enterprise-attack.json"

    if filepath.exists() and not force:
        logger.info("Using cached ATT&CK data", path=str(filepath))
        return filepath

    logger.info("Downloading MITRE ATT&CK Enterprise data...")
    response = httpx.get(ATTACK_URL, timeout=60)
    response.raise_for_status()

    filepath.write_bytes(response.content)
    logger.info("ATT&CK data downloaded", size_mb=round(len(response.content) / 1e6, 1))
    return filepath


def parse_techniques(filepath: Path) -> list[dict]:
    """Parse ATT&CK JSON and extract technique entries.

    Args:
        filepath: Path to the enterprise-attack.json file.

    Returns:
        List of technique dicts with id, name, description, tactic, platform.
    """
    data = json.loads(filepath.read_text(encoding="utf-8"))
    objects = data.get("objects", [])

    techniques = []
    for obj in objects:
        if obj.get("type") != "attack-pattern":
            continue
        if obj.get("revoked", False) or obj.get("x_mitre_deprecated", False):
            continue

        # Extract technique ID from external references
        technique_id = ""
        url = ""
        for ref in obj.get("external_references", []):
            if ref.get("source_name") == "mitre-attack":
                technique_id = ref.get("external_id", "")
                url = ref.get("url", "")
                break

        if not technique_id:
            continue

        # Extract tactics from kill chain phases
        tactics = [
            phase.get("phase_name", "")
            for phase in obj.get("kill_chain_phases", [])
            if phase.get("kill_chain_name") == "mitre-attack"
        ]

        # Extract platforms
        platforms = obj.get("x_mitre_platforms", [])

        name = obj.get("name", "")
        description = obj.get("description", "")

        # Create one entry per tactic (a technique can appear in multiple tactics)
        for tactic in tactics or ["unknown"]:
            techniques.append({
                "technique_id": technique_id,
                "name": name,
                "description": description[:2000],
                "tactic": tactic,
                "platform": ", ".join(platforms),
                "url": url,
            })

    logger.info("Parsed ATT&CK techniques", count=len(techniques))
    return techniques


def ingest_techniques(techniques: list[dict]) -> None:
    """Ingest parsed techniques into ChromaDB vector store.

    Args:
        techniques: List of technique dicts from parse_techniques().
    """
    documents = []
    metadatas = []
    ids = []

    for tech in techniques:
        # Create a rich document combining name, tactic, and description
        doc_text = (
            f"MITRE ATT&CK Technique: {tech['technique_id']} - {tech['name']}\n"
            f"Tactic: {tech['tactic']}\n"
            f"Platforms: {tech['platform']}\n"
            f"Description: {tech['description']}"
        )

        doc_id = f"{tech['technique_id']}_{tech['tactic']}"

        documents.append(doc_text)
        metadatas.append({
            "technique_id": tech["technique_id"],
            "name": tech["name"],
            "tactic": tech["tactic"],
            "platform": tech["platform"],
            "url": tech["url"],
        })
        ids.append(doc_id)

    # Batch insert (ChromaDB handles batching internally)
    batch_size = 100
    for i in range(0, len(documents), batch_size):
        batch_docs = documents[i:i + batch_size]
        batch_meta = metadatas[i:i + batch_size]
        batch_ids = ids[i:i + batch_size]
        add_documents(batch_docs, batch_meta, batch_ids)

    logger.info("Ingestion complete", total_documents=len(documents))


def run_ingestion(force_download: bool = False, reset: bool = False) -> int:
    """Run the full MITRE ATT&CK ingestion pipeline.

    Args:
        force_download: Force re-download of ATT&CK data.
        reset: Reset the collection before ingestion.

    Returns:
        Number of techniques ingested.
    """
    if reset:
        reset_collection()

    collection = get_collection()
    if collection.count() > 0 and not reset:
        logger.info(
            "Collection already populated, skipping ingestion",
            count=collection.count(),
        )
        return collection.count()

    filepath = download_attack_data(force=force_download)
    techniques = parse_techniques(filepath)
    ingest_techniques(techniques)
    return len(techniques)


if __name__ == "__main__":
    setup_logging("INFO")
    count = run_ingestion(reset=True)
    print(f"Ingested {count} MITRE ATT&CK technique entries into ChromaDB.")
