"""
SOCsentinel — Report Writer API router.
"""

from fastapi import APIRouter
from pydantic import BaseModel

from app.shared.schemas import APIResponse
from app.features.report_writer.service import generate_report


class ReportRequest(BaseModel):
    """Request body for report generation."""
    alert_data: dict
    triage_result: dict | None = None
    evidence_result: dict | None = None
    mitre_result: dict | None = None


router = APIRouter(prefix="/report", tags=["Report Writer Agent"])


@router.post("/generate", response_model=APIResponse)
async def generate_report_endpoint(request: ReportRequest) -> APIResponse:
    """Generate an investigation report from all agent outputs.

    Synthesizes triage, evidence, and MITRE mapping results
    into a comprehensive, actionable report.
    """
    result = await generate_report(
        alert_data=request.alert_data,
        triage_result=request.triage_result,
        evidence_result=request.evidence_result,
        mitre_result=request.mitre_result,
    )
    return APIResponse(
        success=True,
        message="Investigation report generated",
        data=result,
    )
