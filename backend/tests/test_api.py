import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "online"

@pytest.mark.asyncio
async def test_api_v1_health():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

@pytest.mark.asyncio
async def test_runner_single():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = {
            "code": "print(2 + 2)",
            "language": "python",
            "input": ""
        }
        response = await client.post("/api/v1/runner/run-single", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["stdout"] == "4"
        assert data["status"] == "COMPLETED"

@pytest.mark.asyncio
async def test_code_review_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = {
            "code": "def solve(n):\n    return n * 2",
            "language": "python",
            "problemTitle": "Double Number",
            "testCases": [
                {"input": "5", "expectedOutput": "10"}
            ]
        }
        response = await client.post("/api/v1/reviews", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "rating" in data
        assert "verdict" in data
        assert "complexityComparison" in data
