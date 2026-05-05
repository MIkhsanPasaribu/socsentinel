"""
SOCsentinel — Evidence Collector API router.
"""

from fastapi import APIRouter

from app.shared.schemas import AlertInput, APIResponse
from app.features.evidence.service import collect_evidence

router = APIRouter(prefix="/evidence", tags=["Evidence Collector Agent"])


@router.post("/collect", response_model=APIResponse)
async def collect_evidence_endpoint(alert: AlertInput) -> APIResponse:
    """Collect and enrich evidence for an alert.

    Gathers IOCs, threat intel, CVE matches, and SIEM correlations.
    """
    result = await collect_evidence(alert)
    return APIResponse(
        success=True,
        message="Evidence collected successfully",
        data=result,
    )
