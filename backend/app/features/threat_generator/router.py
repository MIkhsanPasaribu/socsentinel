"""
SOCsentinel — Threat Generator API router.
"""

from fastapi import APIRouter

from app.shared.schemas import APIResponse
from app.features.threat_generator.schemas import ThreatScenarioInput
from app.features.threat_generator.service import generate_threat_scenario

router = APIRouter(prefix="/threat-generator", tags=["Threat Generator"])


@router.post("/generate", response_model=APIResponse)
async def generate_threat_scenario_endpoint(
    payload: ThreatScenarioInput,
) -> APIResponse:
    """Generate a threat scenario from a MITRE ATT&CK technique."""
    result = await generate_threat_scenario(
        technique_id=payload.technique_id,
        apt_group=payload.apt_group,
        additional_context={
            "target_sector": payload.target_sector,
        },
        include_threat_intel=payload.include_threat_intel,
        intel_keywords=payload.intel_keywords,
    )
    return APIResponse(
        success=True,
        message="Threat scenario generated",
        data=result,
    )
