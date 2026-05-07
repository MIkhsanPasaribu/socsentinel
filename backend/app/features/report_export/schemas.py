"""
SOCsentinel — Report Export schemas.

Pydantic models for request/response validation.
"""

from pydantic import BaseModel


class ExportStatus(BaseModel):
    """Status of an export operation."""
    investigation_id: str
    format: str  # "pdf" or "docx"
    status: str  # "pending", "generating", "completed", "failed"
    message: str = ""
