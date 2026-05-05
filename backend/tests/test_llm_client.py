"""
SOCsentinel — Unit tests for LLM client.
"""

import pytest
from app.shared.llm.client import MockChatModel, create_llm_client
from langchain_core.messages import HumanMessage, SystemMessage


class TestMockChatModel:
    """Test the MockChatModel used for dev/testing."""

    def test_orchestrator_response(self):
        model = MockChatModel()
        messages = [
            SystemMessage(content="You are the SOCsentinel Orchestrator Agent"),
            HumanMessage(content="Analyze this alert"),
        ]
        result = model.invoke(messages)
        assert "alert_id" in result.content
        assert "assigned_agent" in result.content

    def test_triage_response(self):
        model = MockChatModel()
        messages = [
            SystemMessage(content="You are the SOCsentinel L1 Triage Agent"),
            HumanMessage(content="Classify this alert"),
        ]
        result = model.invoke(messages)
        assert "classification" in result.content
        assert "evidence_chain" in result.content

    def test_evidence_response(self):
        model = MockChatModel()
        messages = [
            SystemMessage(content="You are the SOCsentinel Evidence Collector Agent"),
            HumanMessage(content="Collect evidence"),
        ]
        result = model.invoke(messages)
        assert "iocs" in result.content
        assert "enrichment_summary" in result.content

    def test_mitre_response(self):
        model = MockChatModel()
        messages = [
            SystemMessage(content="You are the SOCsentinel MITRE Mapper Agent"),
            HumanMessage(content="Map techniques"),
        ]
        result = model.invoke(messages)
        assert "techniques" in result.content
        assert "kill_chain_phase" in result.content

    def test_report_response(self):
        model = MockChatModel()
        messages = [
            SystemMessage(content="You are the SOCsentinel Report Writer Agent"),
            HumanMessage(content="Generate report"),
        ]
        result = model.invoke(messages)
        assert "title" in result.content
        assert "executive_summary" in result.content
        assert "recommendations" in result.content

    def test_fallback_response(self):
        model = MockChatModel()
        messages = [
            SystemMessage(content="You are an unknown agent"),
            HumanMessage(content="Do something"),
        ]
        result = model.invoke(messages)
        assert "response" in result.content


class TestCreateLLMClient:
    """Test LLM client factory."""

    def test_mock_provider(self, monkeypatch):
        monkeypatch.setenv("LLM_PROVIDER", "mock")
        from app.core.config import Settings
        settings = Settings()
        client = create_llm_client(settings=settings)
        assert isinstance(client, MockChatModel)

    def test_unsupported_provider(self, monkeypatch):
        monkeypatch.setenv("LLM_PROVIDER", "unsupported")
        from app.core.config import Settings
        settings = Settings()
        with pytest.raises(ValueError, match="Unsupported"):
            create_llm_client(settings=settings)
