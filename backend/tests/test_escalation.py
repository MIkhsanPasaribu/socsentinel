"""
SOCsentinel — Unit tests for escalation rules engine.
"""

from app.shared.utils.escalation import determine_escalation_level, EscalationLevel


class TestEscalationRules:
    def test_false_positive_closes(self):
        result = determine_escalation_level("low", triage_classification="close")
        assert result["level"] == EscalationLevel.L1
        assert result["action"] == "close"

    def test_low_severity_stays_l1(self):
        result = determine_escalation_level("low", triage_classification="investigate")
        assert result["level"] == EscalationLevel.L1
        assert result["auto_escalated"] is False

    def test_high_severity_escalates_l2(self):
        result = determine_escalation_level("high")
        assert result["level"] == EscalationLevel.L2
        assert result["auto_escalated"] is True
        assert "high" in result["reason"]

    def test_critical_severity_escalates_l2(self):
        result = determine_escalation_level("critical")
        assert result["level"] == EscalationLevel.L2

    def test_explicit_escalation(self):
        result = determine_escalation_level("medium", triage_classification="escalate")
        assert result["level"] == EscalationLevel.L2
        assert "explicitly escalated" in result["reason"]

    def test_low_confidence_escalates(self):
        result = determine_escalation_level("medium", triage_confidence=0.3)
        assert result["level"] == EscalationLevel.L2
        assert "Low triage confidence" in result["reason"]

    def test_many_techniques_escalates_l3(self):
        result = determine_escalation_level("high", technique_count=4)
        assert result["level"] == EscalationLevel.L3
        assert "4 MITRE" in result["reason"]

    def test_late_stage_kill_chain_escalates_l3(self):
        result = determine_escalation_level(
            "high", kill_chain_phase="exfiltration"
        )
        assert result["level"] == EscalationLevel.L3
        assert "exfiltration" in result["reason"]

    def test_medium_stays_l1(self):
        result = determine_escalation_level(
            "medium", triage_classification="investigate", triage_confidence=0.75
        )
        assert result["level"] == EscalationLevel.L1
        assert result["auto_escalated"] is False

    def test_combined_escalation(self):
        """Critical + many techniques → L3 with multiple reasons."""
        result = determine_escalation_level(
            "critical", technique_count=5, kill_chain_phase="impact"
        )
        assert result["level"] == EscalationLevel.L3
        assert result["auto_escalated"] is True
