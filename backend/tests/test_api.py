"""
SOCsentinel — API integration tests.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "socsentinel-backend"


@pytest.mark.asyncio
async def test_generate_alert_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/v1/alerts/generate?scenario=brute_force")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["severity"] == "high"


@pytest.mark.asyncio
async def test_generate_batch_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/v1/alerts/generate-batch?count=3")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]) == 3


@pytest.mark.asyncio
async def test_pipeline_demo_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/pipeline/investigate-demo?scenario=brute_force"
        )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["status"] == "completed"
    assert data["meta"]["investigation_id"].startswith("INV-")


@pytest.mark.asyncio
async def test_detection_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/detection/generate",
            json={
                "alert_data": {"alert_id": "ALERT-MOCK-001"},
                "mitre_result": {"techniques": [{"technique_id": "T1110"}]},
                "evidence_result": {"iocs": []},
            },
        )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "sigma_rule" in data["data"]


@pytest.mark.asyncio
async def test_response_planner_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/response-planner/generate",
            json={
                "alert_data": {"alert_id": "ALERT-MOCK-001"},
                "triage_result": {"classification": "investigate"},
                "evidence_result": {"iocs": []},
                "mitre_result": {"techniques": []},
                "report_result": {"title": "Mock"},
            },
        )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["playbook_name"]


@pytest.mark.asyncio
async def test_validator_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/validator/validate",
            json={
                "alert_data": {"alert_id": "ALERT-MOCK-001"},
                "playbook_result": {"playbook_name": "Mock"},
            },
        )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "is_approved" in data["data"]


@pytest.mark.asyncio
async def test_threat_generator_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/threat-generator/generate",
            json={
                "technique_id": "T1110",
                "apt_group": "generic",
                "target_sector": "general",
                "include_threat_intel": False,
            },
        )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["scenario_name"]


@pytest.mark.asyncio
async def test_soar_export_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/soar/export",
            json={
                "platform": "generic",
                "investigation_id": "INV-MOCK-001",
                "payload": {"alert": {"severity": "low"}},
            },
        )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["platform"] == "generic"


@pytest.mark.asyncio
async def test_pipeline_list_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/pipeline/list")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


@pytest.mark.asyncio
async def test_openapi_docs():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert "SOCsentinel" in schema["info"]["title"]
