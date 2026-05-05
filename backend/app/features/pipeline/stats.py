"""
SOCsentinel — Pipeline statistics service.

Aggregates investigation metrics for the dashboard.
"""

from typing import Any

from app.features.pipeline.service import _pipeline_store
from app.shared.schemas import InvestigationStatus


def get_pipeline_stats() -> dict[str, Any]:
    """Compute aggregate pipeline statistics from in-memory store.

    Returns:
        Dict with total_investigations, avg_processing_time_ms,
        investigations_by_severity, agent_performance, etc.
    """
    investigations = list(_pipeline_store.values())
    total = len(investigations)

    if total == 0:
        return {
            "total_investigations": 0,
            "completed": 0,
            "failed": 0,
            "avg_processing_time_ms": 0,
            "total_alerts_today": 0,
            "auto_triaged": 0,
            "false_positive_rate": 0,
            "escalation_rate": 0,
            "investigations_by_severity": {},
            "agent_performance": [],
        }

    completed = [s for s in investigations if s.status == InvestigationStatus.COMPLETED]
    failed = [s for s in investigations if s.status == InvestigationStatus.FAILED]

    # Average processing time
    times = [s.total_processing_time_ms for s in completed if s.total_processing_time_ms > 0]
    avg_time = round(sum(times) / len(times), 1) if times else 0

    # Severity distribution
    severity_counts: dict[str, int] = {}
    for s in investigations:
        sev = s.alert.severity.value
        severity_counts[sev] = severity_counts.get(sev, 0) + 1

    # False positive rate (triage says "close")
    false_positives = 0
    escalations = 0
    for s in completed:
        if s.triage_result:
            classification = s.triage_result.get("classification", "")
            if classification == "close":
                false_positives += 1
            elif classification == "escalate":
                escalations += 1

    fp_rate = round(false_positives / len(completed) * 100, 1) if completed else 0
    esc_rate = round(escalations / len(completed) * 100, 1) if completed else 0

    # Agent performance breakdown
    agent_times: dict[str, list[float]] = {}
    for s in completed:
        for entry in s.audit_trail:
            agent = entry.get("agent", "Unknown")
            t = entry.get("processing_time_ms", 0)
            if agent not in agent_times:
                agent_times[agent] = []
            agent_times[agent].append(t)

    agent_performance = []
    for agent, times_list in agent_times.items():
        agent_performance.append({
            "agent": agent,
            "avg_time_ms": round(sum(times_list) / len(times_list), 1),
            "total_runs": len(times_list),
            "max_time_ms": round(max(times_list), 1),
            "min_time_ms": round(min(times_list), 1),
        })

    return {
        "total_investigations": total,
        "completed": len(completed),
        "failed": len(failed),
        "avg_processing_time_ms": avg_time,
        "total_alerts_today": total,
        "auto_triaged": len(completed),
        "auto_triage_rate": round(len(completed) / total * 100, 1) if total else 0,
        "false_positive_rate": fp_rate,
        "escalation_rate": esc_rate,
        "investigations_by_severity": severity_counts,
        "agent_performance": agent_performance,
    }
