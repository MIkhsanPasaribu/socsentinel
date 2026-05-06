"""
SOCsentinel — SOAR integration schemas.
"""

from typing import Any

from pydantic import BaseModel, Field


class SOARExportRequest(BaseModel):
    """Request payload for exporting investigation results to SOAR."""

    platform: str = Field(description="Target SOAR: splunk|xsoar|sentinel|generic")
    investigation_id: str = Field(description="Investigation identifier")
    payload: dict[str, Any] | None = Field(
        default=None,
        description="Investigation payload to export",
    )


class SOARExportResponse(BaseModel):
    """Response payload for SOAR export."""

    platform: str
    export_payload: dict[str, Any]
