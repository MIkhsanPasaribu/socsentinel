"""
SOCsentinel — SOAR integration API router.
"""

from fastapi import APIRouter

from app.shared.schemas import APIResponse
from app.features.soar_integration.schemas import SOARExportRequest
from app.features.soar_integration.service import export_to_soar

router = APIRouter(prefix="/soar", tags=["SOAR Integration"])


@router.post("/export", response_model=APIResponse)
async def export_to_soar_endpoint(payload: SOARExportRequest) -> APIResponse:
    """Export investigation results to a SOAR platform."""
    export_payload = export_to_soar(
        platform=payload.platform,
        investigation_id=payload.investigation_id,
        payload=payload.payload,
    )
    return APIResponse(
        success=True,
        message="SOAR export generated",
        data={
            "platform": payload.platform,
            "export_payload": export_payload,
        },
    )


@router.post("/export/{investigation_id}", response_model=APIResponse)
async def export_to_soar_by_id(
    investigation_id: str,
    platform: str = "generic",
) -> APIResponse:
    """Export stored investigation results to a SOAR platform."""
    export_payload = export_to_soar(
        platform=platform,
        investigation_id=investigation_id,
        payload=None,
    )
    return APIResponse(
        success=True,
        message="SOAR export generated",
        data={
            "platform": platform,
            "export_payload": export_payload,
        },
    )
