"""
SOCsentinel — Integration tests for pipeline.
"""

import pytest
from app.features.alerts.generator import generate_alert
from app.features.pipeline.service import run_investigation, get_investigation, list_investigations


@pytest.mark.asyncio
async def test_full_pipeline_brute_force():
    """Test full pipeline with brute force scenario."""
    alert = generate_alert("brute_force")
    state = await run_investigation(alert)

    assert state.investigation_id.startswith("INV-")
    assert state.status.value == "completed"
    assert state.orchestrator_result is not None
    assert state.triage_result is not None
    assert state.evidence_result is not None
    assert state.mitre_result is not None
    assert state.detection_result is not None
    assert state.report_result is not None
    assert state.response_result is not None
    assert state.validator_result is not None
    # 8 agent steps + escalation entries
    assert len(state.audit_trail) >= 9
    assert state.total_processing_time_ms > 0


@pytest.mark.asyncio
async def test_full_pipeline_ransomware():
    """Test full pipeline with ransomware scenario."""
    alert = generate_alert("ransomware")
    state = await run_investigation(alert)

    assert state.status.value == "completed"
    assert state.detection_result is not None
    assert state.report_result is not None
    assert state.report_result.get("_agent") == "Report Writer"


@pytest.mark.asyncio
async def test_pipeline_audit_trail():
    """Verify audit trail records all agent steps."""
    alert = generate_alert("phishing")
    state = await run_investigation(alert)

    agents = [e["agent"] for e in state.audit_trail]
    assert "Orchestrator" in agents
    assert "L1 Triage" in agents
    assert "Evidence Collector" in agents
    assert "MITRE Mapper" in agents
    assert "Detection" in agents
    assert "Report Writer" in agents
    assert "Response Planner" in agents
    assert "Validator" in agents

    for entry in state.audit_trail:
        assert entry["status"] == "completed"
        # Escalation entries don't have processing_time_ms
        if entry["step"] not in ("escalation_check", "escalation_upgrade"):
            assert entry["processing_time_ms"] >= 0


@pytest.mark.asyncio
async def test_get_investigation():
    """Test investigation retrieval by ID."""
    alert = generate_alert("lateral_movement")
    state = await run_investigation(alert)

    retrieved = get_investigation(state.investigation_id)
    assert retrieved is not None
    assert retrieved.investigation_id == state.investigation_id


@pytest.mark.asyncio
async def test_list_investigations():
    """Test investigation listing."""
    alert = generate_alert("data_exfiltration")
    state = await run_investigation(alert)

    investigations = list_investigations()
    assert len(investigations) > 0
    ids = [inv["investigation_id"] for inv in investigations]
    assert state.investigation_id in ids
