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
