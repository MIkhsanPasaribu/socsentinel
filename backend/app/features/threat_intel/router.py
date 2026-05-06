"""
SOCsentinel — Threat intel API router.
"""

from fastapi import APIRouter

from app.shared.schemas import APIResponse
from app.features.threat_intel.schemas import ThreatIntelRequest
from app.features.threat_intel.service import fetch_threat_intel

router = APIRouter(prefix="/threat-intel", tags=["Threat Intel"])


@router.post("/fetch", response_model=APIResponse)
async def fetch_threat_intel_endpoint(payload: ThreatIntelRequest) -> APIResponse:
    """Fetch threat intel from a TAXII server."""
    result = await fetch_threat_intel(
        server_url=payload.server_url,
        api_root=payload.api_root,
        collection_id=payload.collection_id,
        token=payload.token,
    )
    return APIResponse(
        success=True,
        message="Threat intel fetched",
        data=result,
    )
