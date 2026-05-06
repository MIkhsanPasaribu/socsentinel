"""
SOCsentinel — Response Planner API router.
"""

from fastapi import APIRouter

from app.shared.schemas import APIResponse
from app.features.response_planner.schemas import ResponsePlaybookRequest
from app.features.response_planner.service import generate_playbook

router = APIRouter(prefix="/response-planner", tags=["Response Planner"])


@router.post("/generate", response_model=APIResponse)
async def generate_playbook_endpoint(payload: ResponsePlaybookRequest) -> APIResponse:
    """Generate a response playbook from investigation outputs."""
    result = await generate_playbook(
        alert_data=payload.alert_data,
        triage_result=payload.triage_result,
        evidence_result=payload.evidence_result,
        mitre_result=payload.mitre_result,
        report_result=payload.report_result,
    )
    return APIResponse(
        success=True,
        message="Response playbook generated",
        data=result,
    )
