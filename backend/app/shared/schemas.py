"""
SOCsentinel — Shared Pydantic schemas.

Common data models used across multiple features/agents.
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


# === Enums ===

class Severity(str, Enum):
    """Alert severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class TriageClassification(str, Enum):
    """L1 triage classification outcomes."""
    INVESTIGATE = "investigate"
    CLOSE = "close"
    ESCALATE = "escalate"


class InvestigationStatus(str, Enum):
    """End-to-end investigation status."""
    PENDING = "pending"
    TRIAGING = "triaging"
    COLLECTING_EVIDENCE = "collecting_evidence"
    MAPPING_MITRE = "mapping_mitre"
    GENERATING_REPORT = "generating_report"
    COMPLETED = "completed"
    FAILED = "failed"


class IOCType(str, Enum):
    """Indicator of Compromise types."""
    IP = "ip"
    DOMAIN = "domain"
    HASH = "hash"
    URL = "url"
    EMAIL = "email"


# === Base Models ===

class APIResponse(BaseModel):
    """Standard API response wrapper."""
    success: bool
    message: str
    data: Any | None = None
    error: dict | None = None
    meta: dict | None = None


class EvidenceStep(BaseModel):
    """A single step in an agent's evidence/reasoning chain."""
    step: str
    observation: str
    conclusion: str


class IOC(BaseModel):
    """Indicator of Compromise."""
    type: IOCType
    value: str
    reputation: str = "unknown"
    source: str = ""
    context: str = ""


class MITRETechnique(BaseModel):
    """A mapped MITRE ATT&CK technique."""
    technique_id: str
    technique_name: str
    tactic: str
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: str = ""


class TimelineEvent(BaseModel):
    """An event in the attack timeline."""
    timestamp: str
    event: str
    technique: str = ""
    tactic: str = ""


# === Alert Models ===

class AlertInput(BaseModel):
    """Raw SIEM alert input."""
    alert_id: str = ""
    source: str = "siem"
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    rule_name: str = ""
    severity: Severity = Severity.MEDIUM
    description: str = ""
    source_ip: str = ""
    destination_ip: str = ""
    source_port: int | None = None
    destination_port: int | None = None
    protocol: str = ""
    username: str = ""
    hostname: str = ""
    raw_log: str = ""
    metadata: dict = Field(default_factory=dict)


# === Pipeline State ===

class PipelineState(BaseModel):
    """Full state of an investigation pipeline run."""
    investigation_id: str = ""
    alert: AlertInput
    status: InvestigationStatus = InvestigationStatus.PENDING
    started_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    completed_at: str | None = None

    # Agent outputs (filled progressively)
    orchestrator_result: dict | None = None
    triage_result: dict | None = None
    evidence_result: dict | None = None
    mitre_result: dict | None = None
    report_result: dict | None = None

    # Escalation & Human Decision
    escalation_result: dict | None = None
    analyst_decision: dict | None = None

    # Audit
    audit_trail: list[dict] = Field(default_factory=list)
    total_processing_time_ms: float = 0.0

