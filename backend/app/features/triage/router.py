"""
SOCsentinel — L1 Triage API router.
"""

from fastapi import APIRouter

from app.shared.schemas import AlertInput, APIResponse
from app.features.triage.service import classify_alert

router = APIRouter(prefix="/triage", tags=["L1 Triage Agent"])


@router.post("/classify", response_model=APIResponse)
async def classify_alert_endpoint(alert: AlertInput) -> APIResponse:
    """Classify an alert through the L1 Triage agent.

    Returns severity assessment, false positive analysis,
    and recommended action (investigate/close/escalate).
    """
    result = await classify_alert(alert)
    return APIResponse(
        success=True,
        message="Alert classified successfully",
        data=result,
    )
