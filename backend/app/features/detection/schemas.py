"""
SOCsentinel — Detection Agent schemas.
"""

from pydantic import BaseModel, Field


class DetectionRule(BaseModel):
    """A generated Sigma detection rule."""
    title: str = Field(description="Human-readable rule title")
    name: str = Field(description="Unique rule identifier (snake_case)")
    status: str = Field(description="Rule status: stable|test|experimental")
    level: str = Field(description="Detection level: informational|low|medium|high|critical")
    description: str = Field(description="What this rule detects")
    tags: list[str] = Field(default_factory=list, description="MITRE ATT&CK tags")
    logsource_product: str = Field(description="SIEM product (e.g., windows, linux)")
    logsource_service: str = Field(description="Service name (e.g., sysmon, apache)")
    detection_selection: dict = Field(description="Detection selection criteria")
    detection_condition: str = Field(description="Detection condition expression")
    fields: list[str] = Field(default_factory=list, description="Fields to extract")
    falsepositives: list[str] = Field(default_factory=list, description="Known false positive scenarios")


class DetectionInput(BaseModel):
    """Input for generating a detection rule."""

    alert_data: dict = Field(description="Original alert data payload")
    mitre_result: dict = Field(description="MITRE ATT&CK mapping result")
    evidence_result: dict | None = Field(
        default=None, description="Evidence collector output"
    )


class DetectionOutput(BaseModel):
    """Output from the Detection Agent."""
    alert_id: str
    sigma_rule: str = Field(description="Complete Sigma rule in YAML format")
    mitre_techniques_mapped: list[str] = Field(description="Technique IDs used in rule")
    detection_logic: str = Field(description="Explanation of detection approach")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence in rule quality")
    false_positive_risk: str = Field(description="low|medium|high")
    recommended_log_sources: list[str] = Field(description="Required log sources for detection")