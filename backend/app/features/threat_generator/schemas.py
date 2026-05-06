"""
SOCsentinel — Threat Generator schemas.
"""

from pydantic import BaseModel, Field


class ThreatScenarioInput(BaseModel):
    """Input for generating a threat scenario."""
    technique_id: str = Field(description="MITRE ATT&CK technique ID (e.g., T1110)")
    apt_group: str = Field(default="generic", description="APT group name (optional)")
    target_sector: str = Field(default="general", description="Target industry sector")
    include_threat_intel: bool = Field(
        default=False, description="Enrich scenario with threat intel context"
    )
    intel_keywords: list[str] = Field(
        default_factory=list, description="Keywords for threat intel lookup"
    )


class ThreatActorStep(BaseModel):
    """A single step in the attack chain."""
    step: int = Field(description="Step number in the attack chain")
    phase: str = Field(description="MITRE ATT&CK tactic")
    technique_id: str = Field(description="Technique ID")
    technique_name: str = Field(description="Technique name")
    description: str = Field(description="How the attacker performs this step")
    expected_telemetry: list[str] = Field(description="What SIEM would see")
    detection_opportunity: str = Field(description="Where SOC could detect")


class ThreatIOC(BaseModel):
    """An IOC associated with the threat scenario."""
    type: str = Field(description="IOC type: ip, domain, hash, url, email")
    value: str = Field(description="IOC value")
    role: str = Field(description="Role in the scenario")


class ThreatScenarioOutput(BaseModel):
    """Output from the Threat Generator."""
    scenario_name: str = Field(description="Descriptive scenario name")
    threat_group: str = Field(description="APT group or 'generic'")
    intent: str = Field(description="Attack objective")
    attack_chain: list[ThreatActorStep] = Field(description="Attack steps")
    iocs: list[ThreatIOC] = Field(description="Indicators of compromise")
    simulation_commands: list[str] = Field(description="Commands to simulate")
    detection_difficulty: str = Field(description="easy|medium|hard")
    confidence: float = Field(ge=0.0, le=1.0)