"""
SOCsentinel — MITRE ATT&CK Heatmap Stats.

Aggregates MITRE techniques from all completed investigations to generate
a heatmap visualization for the dashboard.
"""

from typing import Any
from app.features.pipeline.service import _pipeline_store
from app.shared.schemas import InvestigationStatus

# The 14 tactics in the MITRE ATT&CK Enterprise Matrix
MITRE_TACTICS = [
    "Initial Access",
    "Execution",
    "Persistence",
    "Privilege Escalation",
    "Defense Evasion",
    "Credential Access",
    "Discovery",
    "Lateral Movement",
    "Collection",
    "Command and Control",
    "Exfiltration",
    "Impact",
]

def get_mitre_heatmap() -> dict[str, Any]:
    """Calculate technique density per tactic across all investigations.
    
    Returns:
        Dict mapping tactic names to a list of detected techniques and their counts.
    """
    heatmap: dict[str, dict[str, int]] = {tactic: {} for tactic in MITRE_TACTICS}
    total_techniques_mapped = 0
    
    # Also track standalone techniques that don't specify a tactic
    heatmap["Uncategorized"] = {}

    investigations = [s for s in _pipeline_store.values() if s.status == InvestigationStatus.COMPLETED]

    for inv in investigations:
        if not inv.mitre_result or "techniques" not in inv.mitre_result:
            continue
            
        techniques = inv.mitre_result["techniques"]
        for tech in techniques:
            tech_id = tech.get("technique_id", tech.get("id", "Unknown"))
            tactic = tech.get("tactic", "Uncategorized")
            
            # Normalize tactic name (sometimes agents return lowercase or underscore)
            normalized_tactic = "Uncategorized"
            for t in MITRE_TACTICS:
                if t.lower() in tactic.lower().replace("_", " "):
                    normalized_tactic = t
                    break
                    
            if tech_id not in heatmap[normalized_tactic]:
                heatmap[normalized_tactic][tech_id] = 0
            heatmap[normalized_tactic][tech_id] += 1
            total_techniques_mapped += 1

    # Format for frontend consumption
    formatted_heatmap = []
    for tactic, techniques in heatmap.items():
        if tactic == "Uncategorized" and not techniques:
            continue
            
        formatted_heatmap.append({
            "tactic": tactic,
            "techniques": [{"id": k, "count": v} for k, v in techniques.items()],
            "total_count": sum(techniques.values())
        })

    return {
        "tactics": formatted_heatmap,
        "total_techniques_mapped": total_techniques_mapped,
        "total_investigations_analyzed": len(investigations)
    }
