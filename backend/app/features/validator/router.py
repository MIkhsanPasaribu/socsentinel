"""
SOCsentinel — Validator API router.
"""

from fastapi import APIRouter

from app.shared.schemas import APIResponse
from app.features.validator.schemas import ValidatorRequest
from app.features.validator.service import validate_playbook

router = APIRouter(prefix="/validator", tags=["Validator"])


@router.post("/validate", response_model=APIResponse)
async def validate_playbook_endpoint(payload: ValidatorRequest) -> APIResponse:
    """Validate a response playbook and return critic feedback."""
    result = await validate_playbook(
        alert_data=payload.alert_data,
        playbook_result=payload.playbook_result,
    )
    return APIResponse(
        success=True,
        message="Playbook validation completed",
        data=result,
    )
