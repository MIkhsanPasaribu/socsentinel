"""
SOCsentinel — Pipeline API router.
"""

from fastapi import APIRouter

from app.shared.schemas import AlertInput, APIResponse
from app.shared.exceptions.base import NotFoundError
from app.features.pipeline.service import (
    run_investigation,
    get_investigation,
    list_investigations,
)
from app.features.pipeline.stats import get_pipeline_stats
from app.features.pipeline.mitre_stats import get_mitre_heatmap
from app.features.pipeline.thinking import get_thinking_mode, set_thinking_mode
from app.features.alerts.generator import generate_alert

router = APIRouter(prefix="/pipeline", tags=["Investigation Pipeline"])


@router.post("/investigate", response_model=APIResponse)
async def investigate_endpoint(alert: AlertInput) -> APIResponse:
    """Run the full investigation pipeline on an alert.

    Executes: Orchestrator → L1 Triage → Evidence Collector →
    MITRE Mapper → Report Writer.

    Returns the complete pipeline state with all agent results.
    """
    state = await run_investigation(alert)
    return APIResponse(
        success=True,
        message=f"Investigation {state.investigation_id} completed ({state.status.value})",
        data=state.model_dump(),
        meta={
            "investigation_id": state.investigation_id,
            "processing_time_ms": state.total_processing_time_ms,
        },
    )


@router.post("/investigate-demo", response_model=APIResponse)
async def investigate_demo_endpoint(
    scenario: str = "brute_force",
) -> APIResponse:
    """Run a demo investigation with a synthetic alert.

    Generates a synthetic alert and runs the full pipeline.
    Great for demos and testing.
    """
    alert = generate_alert(scenario)
    state = await run_investigation(alert)
    return APIResponse(
        success=True,
        message=f"Demo investigation {state.investigation_id} completed",
        data=state.model_dump(),
        meta={
            "investigation_id": state.investigation_id,
            "scenario": scenario,
            "processing_time_ms": state.total_processing_time_ms,
        },
    )


@router.get("/status/{investigation_id}", response_model=APIResponse)
async def get_status_endpoint(investigation_id: str) -> APIResponse:
    """Get the status and results of an investigation."""
    state = get_investigation(investigation_id)
    if not state:
        raise NotFoundError("Investigation", investigation_id)
    return APIResponse(
        success=True,
        message=f"Investigation {investigation_id} status: {state.status.value}",
        data=state.model_dump(),
    )

@router.get("/list", response_model=APIResponse)
async def list_investigations_endpoint() -> APIResponse:
    """List all investigations with summary information."""
    investigations = list_investigations()
    return APIResponse(
        success=True,
        message=f"Found {len(investigations)} investigations",
        data=investigations,
    )


@router.get("/stats", response_model=APIResponse)
async def stats_endpoint() -> APIResponse:
    """Get aggregate pipeline statistics for the dashboard.

    Returns metrics: total investigations, avg time, severity distribution,
    false positive rate, agent performance breakdown.
    """
    stats = get_pipeline_stats()
    return APIResponse(
        success=True,
        message="Pipeline statistics",
        data=stats,
    )


@router.get("/mitre-heatmap", response_model=APIResponse)
async def mitre_heatmap_endpoint() -> APIResponse:
    """Get MITRE ATT&CK technique density across all investigations."""
    heatmap = get_mitre_heatmap()
    return APIResponse(
        success=True,
        message="MITRE ATT&CK Heatmap Data",
        data=heatmap,
    )


@router.post("/thinking-mode", response_model=APIResponse)
async def toggle_thinking_mode_endpoint(enabled: bool) -> APIResponse:
    """Toggle Qwen3 chain-of-thought thinking mode."""
    result = set_thinking_mode(enabled)
    return APIResponse(
        success=True,
        message=f"Thinking mode {'enabled' if enabled else 'disabled'}",
        data=result,
    )

@router.get("/thinking-mode", response_model=APIResponse)
async def get_thinking_mode_endpoint() -> APIResponse:
    """Get current state of Qwen3 thinking mode."""
    enabled = get_thinking_mode()
    return APIResponse(
        success=True,
        message="Thinking mode status retrieved",
        data={"thinking_mode": enabled},
    )
