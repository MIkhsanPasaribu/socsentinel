"""
SOCsentinel — Threat intel schemas.
"""

from pydantic import BaseModel, Field


class ThreatIntelRequest(BaseModel):
    """Request payload for threat intel retrieval."""

    collection_id: str | None = Field(default=None, description="TAXII collection ID")
    api_root: str = Field(default="", description="API root or index")
    server_url: str | None = Field(default=None, description="TAXII server URL")
    token: str | None = Field(default=None, description="Bearer token")


class ThreatIntelResponse(BaseModel):
    """Normalized threat intel response."""

    indicator_count: int
    attack_pattern_count: int
    relationship_count: int
    indicators: list[dict]
    attack_patterns: list[dict]
