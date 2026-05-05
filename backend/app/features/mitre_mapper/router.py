"""
SOCsentinel — MITRE Mapper API router.
"""

from fastapi import APIRouter

from app.shared.schemas import AlertInput, APIResponse
from app.features.mitre_mapper.service import map_to_attack

router = APIRouter(prefix="/mitre", tags=["MITRE Mapper Agent"])


@router.post("/map", response_model=APIResponse)
async def map_to_attack_endpoint(alert: AlertInput) -> APIResponse:
    """Map alert behaviors to MITRE ATT&CK techniques.

    Uses RAG retrieval from the MITRE ATT&CK knowledge base
    for grounded technique mapping and timeline reconstruction.
    """
    result = await map_to_attack(alert)
    return APIResponse(
        success=True,
        message="MITRE ATT&CK mapping completed",
        data=result,
    )
