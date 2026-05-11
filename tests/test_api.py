import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


class TestAPI:
    def test_root_endpoint(self):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "DealSense AI"
        assert data["version"] == "1.0.0"

    def test_health_endpoint(self):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "services" in data

    def test_analyze_deal_valid_request(self):
        payload = {
            "acquirer": "Microsoft",
            "target": "GitHub",
            "industry": "Software",
            "deal_value_usd": 7500000000,
        }
        response = client.post("/api/v1/analyze-deal", json=payload, timeout=180)
        assert response.status_code in [200, 201]
        data = response.json()
        assert "deal_id" in data
        assert "recommendation" in data
        assert data["acquirer"] == "Microsoft"
        assert data["target"] == "GitHub"
        assert "success_probability" in data
        assert "executive_summary" in data

    def test_analyze_deal_validation_error(self):
        payload = {
            "acquirer": "",
            "target": "GitHub",
            "industry": "Software",
            "deal_value_usd": 7500000000,
        }
        response = client.post("/api/v1/analyze-deal", json=payload)
        assert response.status_code == 422

    def test_analyze_deal_invalid_deal_value(self):
        payload = {
            "acquirer": "Microsoft",
            "target": "GitHub",
            "industry": "Software",
            "deal_value_usd": -100,
        }
        response = client.post("/api/v1/analyze-deal", json=payload)
        assert response.status_code == 422

    def test_get_deal_invalid_uuid(self):
        response = client.get("/api/v1/deal/invalid-uuid")
        assert response.status_code == 400

    def test_api_documentation_available(self):
        response = client.get("/docs")
        assert response.status_code == 200
        response = client.get("/redoc")
        assert response.status_code == 200