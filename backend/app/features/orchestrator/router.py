"""
SOCsentinel — Orchestrator API router.
"""

from fastapi import APIRouter

from app.shared.schemas import AlertInput, APIResponse
from app.features.orchestrator.service import route_alert

router = APIRouter(prefix="/orchestrator", tags=["Orchestrator Agent"])


@router.post("/route", response_model=APIResponse)
async def route_alert_endpoint(alert: AlertInput) -> APIResponse:
    """Route an incoming SIEM alert to the appropriate agent.

    The Orchestrator parses the alert, assigns priority,
    and determines which agent should handle it next.
    """
    result = await route_alert(alert)
    return APIResponse(
        success=True,
        message="Alert routed successfully",
        data=result,
    )
