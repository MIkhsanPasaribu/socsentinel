"""
SOCsentinel — Detection Agent API router.
"""

from fastapi import APIRouter

from app.shared.schemas import APIResponse
from app.features.detection.schemas import DetectionInput
from app.features.detection.service import generate_detection

router = APIRouter(prefix="/detection", tags=["Detection Agent"])


@router.post("/generate", response_model=APIResponse)
async def generate_detection_endpoint(payload: DetectionInput) -> APIResponse:
    """Generate a Sigma detection rule from MITRE ATT&CK mappings.

    Takes the MITRE ATT&CK mapping and IOCs, and produces a deployable
    Sigma rule that can be imported into SIEM platforms like Splunk,
    Elastic, Microsoft Sentinel, and others.

    Args:
        alert_data: Original alert data.
        mitre_result: MITRE ATT&CK mapping result.
        evidence_result: Evidence collector result (optional).

    Returns:
        Sigma rule in YAML format ready for deployment.
    """
    result = await generate_detection(
        alert_data=payload.alert_data,
        mitre_result=payload.mitre_result,
        evidence_result=payload.evidence_result,
    )
    return APIResponse(
        success=True,
        message="Detection rule generated",
        data=result,
    )