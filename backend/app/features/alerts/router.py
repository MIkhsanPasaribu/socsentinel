"""
SOCsentinel — Alerts API router.
"""

from fastapi import APIRouter, Query

from app.shared.schemas import AlertInput, APIResponse
from app.features.alerts.generator import generate_alert, generate_batch

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.post("/generate", response_model=APIResponse)
async def generate_alert_endpoint(
    scenario: str | None = Query(None, description="Attack scenario: brute_force, lateral_movement, data_exfiltration, phishing, ransomware"),
) -> APIResponse:
    """Generate a synthetic SIEM alert for testing.

    Optionally specify a scenario or get a random one.
    """
    alert = generate_alert(scenario)
    return APIResponse(
        success=True,
        message=f"Synthetic alert generated ({alert.metadata.get('scenario', 'random')})",
        data=alert.model_dump(),
    )


@router.post("/generate-batch", response_model=APIResponse)
async def generate_batch_endpoint(
    count: int = Query(5, ge=1, le=20, description="Number of alerts to generate"),
) -> APIResponse:
    """Generate a batch of synthetic alerts for testing."""
    alerts = generate_batch(count)
    return APIResponse(
        success=True,
        message=f"Generated {len(alerts)} synthetic alerts",
        data=[a.model_dump() for a in alerts],
    )
