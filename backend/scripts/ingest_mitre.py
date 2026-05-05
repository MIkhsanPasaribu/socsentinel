"""
SOCsentinel — MITRE ATT&CK Enterprise data ingestion script.

Downloads the full MITRE ATT&CK Enterprise Matrix from the official
MITRE CTI GitHub repository and ingests all techniques into the ChromaDB
vector store for RAG-grounded reasoning.

Usage:
    python -m scripts.ingest_mitre
"""

import json
import os
import sys
import time
import urllib.request
from pathlib import Path

# Add parent dir to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.logger import get_logger
from app.shared.rag.vector_store import get_collection

logger = get_logger(__name__)

MITRE_URL = (
    "https://raw.githubusercontent.com/mitre/cti/master/"
    "enterprise-attack/enterprise-attack.json"
)
CACHE_PATH = Path("data/mitre/enterprise-attack.json")


def download_mitre_data() -> dict:
    """Download MITRE ATT&CK Enterprise JSON (or use cached)."""
    if CACHE_PATH.exists():
        logger.info("Using cached MITRE ATT&CK data", path=str(CACHE_PATH))
        with open(CACHE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    logger.info("Downloading MITRE ATT&CK Enterprise Matrix...", url=MITRE_URL)
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)

    urllib.request.urlretrieve(MITRE_URL, str(CACHE_PATH))
    logger.info(
        "Download complete",
        size_mb=round(CACHE_PATH.stat().st_size / 1024 / 1024, 1),
    )

    with open(CACHE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_techniques(data: dict) -> list[dict]:
    """Extract attack-pattern objects from STIX bundle.

    Returns list of technique dicts with:
    - technique_id (e.g., T1059)
    - name
    - description
    - tactics (list)
    - platforms (list)
    - detection
    - url
    """
    techniques = []

    for obj in data.get("objects", []):
        if obj.get("type") != "attack-pattern":
            continue
        if obj.get("revoked", False) or obj.get("x_mitre_deprecated", False):
            continue

        # Extract technique ID from external references
        ext_refs = obj.get("external_references", [])
        technique_id = ""
        url = ""
        for ref in ext_refs:
            if ref.get("source_name") == "mitre-attack":
                technique_id = ref.get("external_id", "")
                url = ref.get("url", "")
                break

        if not technique_id:
            continue

        # Extract tactics from kill chain phases
        tactics = []
        for phase in obj.get("kill_chain_phases", []):
            if phase.get("kill_chain_name") == "mitre-attack":
                tactics.append(phase.get("phase_name", ""))

        # Extract platforms
        platforms = obj.get("x_mitre_platforms", [])

        techniques.append({
            "technique_id": technique_id,
            "name": obj.get("name", ""),
            "description": obj.get("description", "")[:2000],  # Truncate long descriptions
            "tactics": tactics,
            "platforms": platforms,
            "detection": (obj.get("x_mitre_detection", "") or "")[:1000],
            "url": url,
            "is_subtechnique": obj.get("x_mitre_is_subtechnique", False),
        })

    return techniques


def build_document_text(technique: dict) -> str:
    """Build a rich text document from a technique for embedding."""
    parts = [
        f"MITRE ATT&CK Technique: {technique['technique_id']} - {technique['name']}",
        f"Tactics: {', '.join(technique['tactics'])}",
        f"Platforms: {', '.join(technique['platforms'])}",
        "",
        technique["description"],
    ]
    if technique["detection"]:
        parts.extend(["", f"Detection: {technique['detection']}"])

    return "\n".join(parts)


def ingest_to_chromadb(techniques: list[dict]) -> int:
    """Ingest techniques into ChromaDB collection.

    Returns number of techniques ingested.
    """
    collection = get_collection("mitre_attack")
    logger.info("Starting ChromaDB ingestion", total_techniques=len(techniques))

    # Batch upsert for performance
    batch_size = 50
    total = 0

    for i in range(0, len(techniques), batch_size):
        batch = techniques[i : i + batch_size]

        ids = [t["technique_id"] for t in batch]
        documents = [build_document_text(t) for t in batch]
        metadatas = [
            {
                "technique_id": t["technique_id"],
                "name": t["name"],
                "tactics": ", ".join(t["tactics"]),
                "platforms": ", ".join(t["platforms"]),
                "is_subtechnique": str(t["is_subtechnique"]),
                "url": t["url"],
            }
            for t in batch
        ]

        collection.upsert(ids=ids, documents=documents, metadatas=metadatas)
        total += len(batch)

        progress = round(total / len(techniques) * 100, 1)
        logger.info(
            f"Ingested {total}/{len(techniques)} techniques ({progress}%)"
        )

    return total


def main():
    """Run full MITRE ATT&CK ingestion pipeline."""
    print("=" * 60)
    print("  SOCsentinel -- MITRE ATT&CK Enterprise Ingestion")
    print("=" * 60)

    start = time.time()

    # Step 1: Download
    print("\n[1/3] Downloading MITRE ATT&CK Enterprise Matrix...")
    data = download_mitre_data()

    # Step 2: Extract
    print("[2/3] Extracting techniques from STIX bundle...")
    techniques = extract_techniques(data)
    print(f"  -> Found {len(techniques)} active techniques")

    # Subtechnique breakdown
    main_techniques = [t for t in techniques if not t["is_subtechnique"]]
    sub_techniques = [t for t in techniques if t["is_subtechnique"]]
    print(f"  -> {len(main_techniques)} main techniques + {len(sub_techniques)} sub-techniques")

    # Tactic distribution
    tactic_counts: dict[str, int] = {}
    for t in techniques:
        for tac in t["tactics"]:
            tactic_counts[tac] = tactic_counts.get(tac, 0) + 1
    print("  -> Tactic distribution:")
    for tac, count in sorted(tactic_counts.items(), key=lambda x: -x[1]):
        print(f"     {tac}: {count}")

    # Step 3: Ingest
    print(f"\n[3/3] Ingesting {len(techniques)} techniques into ChromaDB...")
    ingested = ingest_to_chromadb(techniques)

    elapsed = round(time.time() - start, 1)
    print(f"\n[OK] Complete! {ingested} techniques ingested in {elapsed}s")
    print("=" * 60)


if __name__ == "__main__":
    main()
