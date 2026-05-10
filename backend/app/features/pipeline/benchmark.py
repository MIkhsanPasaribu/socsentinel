"""
SOCsentinel — Pipeline benchmark endpoint.

Runs multiple investigation scenarios and reports per-agent
and per-scenario latency metrics. Provides evidence for
"AMD MI300X acceleration" claim in hackathon presentation.
"""

import time
from typing import Any

from fastapi import APIRouter

from app.core.logger import get_logger
from app.shared.schemas import APIResponse
from app.features.alerts.generator import generate_alert
from app.features.pipeline.service import run_investigation

logger = get_logger(__name__)

router = APIRouter(prefix="/pipeline", tags=["Pipeline Benchmark"])

BENCHMARK_SCENARIOS = [
    "brute_force",
    "lateral_movement",
    "data_exfiltration",
    "phishing",
    "ransomware",
]


@router.post("/benchmark", response_model=APIResponse)
async def run_benchmark() -> APIResponse:
    """Run a benchmark across all 5 attack scenarios.

    Returns per-scenario latency, per-agent latency breakdown,
    and aggregate statistics.

    This endpoint exists to generate evidence for the hackathon
    presentation showing AMD MI300X inference performance.
    """
    logger.info("Starting pipeline benchmark", scenarios=len(BENCHMARK_SCENARIOS))

    benchmark_start = time.time()
    results: list[dict[str, Any]] = []

    for scenario in BENCHMARK_SCENARIOS:
        alert = generate_alert(scenario)
        scenario_start = time.time()

        try:
            state = await run_investigation(alert)

            scenario_time = round((time.time() - scenario_start) * 1000, 1)

            # Extract per-agent timing from audit trail
            agent_times: dict[str, float] = {}
            for entry in state.audit_trail:
                if entry.get("processing_time_ms") is not None:
                    agent_times[entry["agent"]] = entry["processing_time_ms"]

            results.append({
                "scenario": scenario,
                "investigation_id": state.investigation_id,
                "status": state.status.value,
                "total_time_ms": scenario_time,
                "agent_times": agent_times,
                "severity": alert.severity.value,
                "escalation_level": (
                    state.escalation_result.get("level", "L1")
                    if state.escalation_result
                    else "L1"
                ),
            })
        except Exception as e:
            logger.error(f"Benchmark scenario '{scenario}' failed: {str(e)}")
            # Skip this scenario and continue with others

    total_benchmark_time = round((time.time() - benchmark_start) * 1000, 1)

    if not results:
        return APIResponse(
            success=False,
            message="All benchmark scenarios failed.",
            error={"detail": "Check backend logs for agent execution errors."}
        )

    # Compute aggregates
    all_times = [r["total_time_ms"] for r in results]
    avg_time = round(sum(all_times) / len(all_times), 1)
    min_time = round(min(all_times), 1)
    max_time = round(max(all_times), 1)

    # Per-agent aggregates
    agent_agg: dict[str, list[float]] = {}
    for r in results:
        for agent, t in r["agent_times"].items():
            if agent not in agent_agg:
                agent_agg[agent] = []
            agent_agg[agent].append(t)

    agent_summary = {
        agent: {
            "avg_ms": round(sum(times) / len(times), 1),
            "min_ms": round(min(times), 1),
            "max_ms": round(max(times), 1),
        }
        for agent, times in agent_agg.items()
    }

    logger.info(
        "Benchmark complete",
        scenarios=len(results),
        avg_time_ms=avg_time,
        total_time_ms=total_benchmark_time,
    )

    return APIResponse(
        success=True,
        message=f"Benchmark complete: {len(results)} scenarios in {total_benchmark_time}ms",
        data={
            "scenarios": results,
            "aggregate": {
                "total_scenarios": len(results),
                "total_time_ms": total_benchmark_time,
                "avg_per_scenario_ms": avg_time,
                "min_scenario_ms": min_time,
                "max_scenario_ms": max_time,
            },
            "agent_performance": agent_summary,
        },
    )
