"""
SOCsentinel — LLM client factory.

Supports two providers:
- 'vllm': Production mode — connects to vLLM serving Qwen3 on AMD MI300X
- 'mock': Development mode — returns deterministic mock responses for testing

Both use the OpenAI-compatible API interface for consistency.
"""

import json
from typing import Any

from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_openai import ChatOpenAI

from app.core.config import Settings, get_settings
from app.core.logger import get_logger

logger = get_logger(__name__)


class MockChatModel(BaseChatModel):
    """Mock LLM for local development without GPU access.

    Returns structured JSON responses that simulate real agent outputs,
    enabling full pipeline testing without LLM infrastructure.
    """

    model_name: str = "mock"

    @property
    def _llm_type(self) -> str:
        return "mock"

    def _generate(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager: CallbackManagerForLLMRun | None = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Generate a mock response based on the system prompt context."""
        system_content = ""
        user_content = ""
        for msg in messages:
            if isinstance(msg, SystemMessage):
                system_content = msg.content
            elif isinstance(msg, HumanMessage):
                user_content = msg.content

        response_text = self._generate_mock_response(system_content, user_content)
        message = AIMessage(content=response_text)
        generation = ChatGeneration(message=message)
        return ChatResult(generations=[generation])

    def _generate_mock_response(self, system: str, user: str) -> str:
        """Generate context-aware mock response based on agent type."""
        # Use only the first 100 chars (identity line) to avoid false matches
        # e.g. Report Writer prompt contains "triage_result" in its JSON spec
        identity = system[:100].lower()

        if "orchestrator" in identity:
            return json.dumps({
                "alert_id": "ALERT-MOCK-001",
                "priority": "high",
                "assigned_agent": "l1_triage",
                "reasoning": "Alert contains indicators of potential brute force attack. Routing to L1 Triage for initial classification.",
                "confidence": 0.85
            })
        elif "triage" in identity:
            return json.dumps({
                "alert_id": "ALERT-MOCK-001",
                "classification": "investigate",
                "severity": "high",
                "is_false_positive": False,
                "confidence": 0.82,
                "reasoning": "Multiple failed login attempts from external IP detected. Pattern consistent with brute force attack.",
                "evidence_chain": [
                    {"step": "Analyzed alert metadata", "observation": "15 failed logins in 2 minutes", "conclusion": "Abnormal login pattern"},
                    {"step": "Checked source IP", "observation": "IP 203.0.113.42 not in allowlist", "conclusion": "External threat actor"}
                ]
            })
        elif "evidence" in identity:
            return json.dumps({
                "alert_id": "ALERT-MOCK-001",
                "iocs": [
                    {"type": "ip", "value": "203.0.113.42", "reputation": "malicious", "source": "AbuseIPDB"},
                    {"type": "domain", "value": "evil-c2.example.com", "reputation": "suspicious", "source": "VirusTotal"}
                ],
                "cve_matches": [],
                "enrichment_summary": "Source IP has been reported 47 times for brute force attacks. Associated domain resolves to known C2 infrastructure.",
                "confidence": 0.88
            })
        elif "mitre" in identity or "att&ck" in identity:
            return json.dumps({
                "alert_id": "ALERT-MOCK-001",
                "techniques": [
                    {"technique_id": "T1110", "technique_name": "Brute Force", "tactic": "Credential Access", "confidence": 0.92},
                    {"technique_id": "T1110.001", "technique_name": "Password Guessing", "tactic": "Credential Access", "confidence": 0.87}
                ],
                "attack_timeline": [
                    {"timestamp": "2026-05-05T10:00:00Z", "event": "Initial brute force attempt detected", "technique": "T1110"},
                    {"timestamp": "2026-05-05T10:02:00Z", "event": "Multiple failed authentications from same source", "technique": "T1110.001"}
                ],
                "kill_chain_phase": "credential_access",
                "confidence": 0.90
            })
        elif "report" in identity:
            return json.dumps({
                "alert_id": "ALERT-MOCK-001",
                "title": "Brute Force Attack Investigation Report",
                "executive_summary": "A brute force attack targeting the authentication system was detected and investigated. The attack originated from IP 203.0.113.42 and involved 15 failed login attempts within 2 minutes.",
                "severity": "high",
                "status": "confirmed_threat",
                "recommendations": [
                    "Block IP 203.0.113.42 at the firewall",
                    "Enable account lockout policy after 5 failed attempts",
                    "Implement MFA for all user accounts",
                    "Monitor for additional activity from associated infrastructure"
                ],
                "confidence": 0.91
            })
        elif "response" in identity or "planner" in identity or "containment" in identity:
            return json.dumps({
                "playbook_name": "Brute Force Containment Playbook",
                "priority": "immediate",
                "containment_status": "not_started",
                "estimated_containment_time": "15 minutes",
                "steps": [
                    {"order": 1, "action": "Block IP 203.0.113.42 at perimeter firewall", "tool": "Firewall API", "risk_level": "low", "automated": True, "details": "Add to blocklist rule set"},
                    {"order": 2, "action": "Force password reset for targeted account admin01", "tool": "Active Directory", "risk_level": "medium", "automated": True, "details": "Trigger immediate password expiry"},
                    {"order": 3, "action": "Enable account lockout after 5 failed attempts", "tool": "Group Policy", "risk_level": "low", "automated": False, "details": "Update GPO lockout threshold"},
                    {"order": 4, "action": "Enable MFA for all domain admin accounts", "tool": "Identity Provider", "risk_level": "low", "automated": False, "details": "Enforce MFA via Conditional Access Policy"},
                    {"order": 5, "action": "Scan for lateral movement from compromised credentials", "tool": "EDR Console", "risk_level": "low", "automated": True, "details": "Run threat hunt query for admin01 activity"}
                ],
                "post_incident": [
                    "Conduct post-incident review within 24 hours",
                    "Update threat intelligence feeds with attacker IOCs",
                    "Review authentication logging coverage",
                    "Schedule security awareness training for targeted team"
                ],
                "confidence": 0.87
            })
        else:
            return json.dumps({
                "response": "Mock response for development",
                "confidence": 0.75
            })


def create_llm_client(
    model_name: str | None = None,
    temperature: float | None = None,
    max_tokens: int | None = None,
    settings: Settings | None = None,
) -> BaseChatModel:
    """Create an LLM client based on the configured provider.

    Args:
        model_name: Override model name. Defaults to config value.
        temperature: Override temperature. Defaults to config value.
        max_tokens: Override max tokens. Defaults to config value.
        settings: Settings override. Defaults to global settings.

    Returns:
        Configured LLM client instance.

    Raises:
        ValueError: If the provider is not supported.
    """
    settings = settings or get_settings()
    temperature = temperature if temperature is not None else settings.llm_temperature
    max_tokens = max_tokens or settings.llm_max_tokens

    if settings.llm_provider == "mock":
        logger.info("Using mock LLM client for development")
        return MockChatModel(model_name=model_name or "mock")

    elif settings.llm_provider == "vllm":
        model = model_name or settings.qwen3_7b_model
        logger.info(
            "Creating vLLM client",
            model=model,
            base_url=settings.vllm_base_url,
        )
        return ChatOpenAI(
            model=model,
            openai_api_key="not-needed",  # vLLM doesn't require API key
            openai_api_base=settings.vllm_base_url,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=settings.llm_request_timeout,
        )

    else:
        raise ValueError(f"Unsupported LLM provider: {settings.llm_provider}")


def get_orchestrator_llm(settings: Settings | None = None) -> BaseChatModel:
    """Get LLM client configured for the Orchestrator agent (Qwen3-7B)."""
    s = settings or get_settings()
    return create_llm_client(model_name=s.qwen3_7b_model, settings=s)


def get_triage_llm(settings: Settings | None = None) -> BaseChatModel:
    """Get LLM client configured for the L1 Triage agent (Qwen3-4B)."""
    s = settings or get_settings()
    return create_llm_client(model_name=s.qwen3_4b_model, settings=s)


def get_evidence_llm(settings: Settings | None = None) -> BaseChatModel:
    """Get LLM client configured for the Evidence Collector agent (Qwen3-7B)."""
    s = settings or get_settings()
    return create_llm_client(model_name=s.qwen3_7b_model, settings=s)


def get_mitre_llm(settings: Settings | None = None) -> BaseChatModel:
    """Get LLM client configured for the MITRE Mapper agent (Qwen3-7B)."""
    s = settings or get_settings()
    return create_llm_client(model_name=s.qwen3_7b_model, settings=s)


def get_report_llm(settings: Settings | None = None) -> BaseChatModel:
    """Get LLM client configured for the Report Writer agent (Qwen3-14B)."""
    s = settings or get_settings()
    return create_llm_client(model_name=s.qwen3_14b_model, settings=s)
