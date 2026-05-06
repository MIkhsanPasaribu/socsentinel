"""
SOCsentinel — Validator schemas.
"""

from typing import Any

from pydantic import BaseModel, Field


class ValidatorRequest(BaseModel):
    """Request payload for validating a response playbook."""

    alert_data: dict[str, Any] = Field(description="Original alert payload")
    playbook_result: dict[str, Any] = Field(description="Response playbook output")


class ValidatorOutput(BaseModel):
    """Validator review output for response playbooks."""

    is_approved: bool = Field(description="Approval flag for the playbook")
    risk_score: float = Field(ge=0.0, le=1.0, description="Business risk score")
    critic_comments: str = Field(description="Detailed review and rationale")
    safe_alternatives: list[str] = Field(description="Safer alternative actions")
    sigma_rule: str = Field(description="Optional Sigma rule in YAML format")
