"""Tests for the Falcon application."""

import json

import falcon.testing
import pytest

from watering.app import create_app
from watering.config import Config


@pytest.fixture
def client(config: Config) -> falcon.testing.TestClient:
    """Create test client for the application."""
    app = create_app(config, use_mock_gpio=True)
    return falcon.testing.TestClient(app)


class TestWateringResource:
    """Tests for watering endpoint."""

    def test_water_success(self, client: falcon.testing.TestClient):
        """Test successful watering request."""
        result = client.simulate_get("/watering.api/water/250")

        assert result.status == falcon.HTTP_200
        data = json.loads(result.text)
        assert data["action"] == "water"
        assert data["volume"] == 250
        assert "duration" in data

    def test_water_invalid_volume(self, client: falcon.testing.TestClient):
        """Test watering with invalid volume."""
        result = client.simulate_get("/watering.api/water/abc")

        assert result.status == falcon.HTTP_400
        assert "error" in result.json

    def test_water_negative_volume(self, client: falcon.testing.TestClient):
        """Test watering with negative volume."""
        result = client.simulate_get("/watering.api/water/-100")

        assert result.status == falcon.HTTP_400
        assert "error" in result.json


class TestFillingResource:
    """Tests for filling endpoint."""

    def test_fill_success(self, client: falcon.testing.TestClient):
        """Test successful filling request."""
        result = client.simulate_get("/watering.api/fill/2000")

        assert result.status == falcon.HTTP_200
        data = json.loads(result.text)
        assert data["action"] == "record_filling"
        assert data["volume"] == 2000

    def test_fill_invalid_volume(self, client: falcon.testing.TestClient):
        """Test filling with invalid volume."""
        result = client.simulate_get("/watering.api/fill/xyz")

        assert result.status == falcon.HTTP_400
        assert "error" in result.json


class TestHistoryResource:
    """Tests for history endpoint."""

    def test_history_empty(self, client: falcon.testing.TestClient):
        """Test history with no data."""
        result = client.simulate_get("/watering.api/history")

        assert result.status == falcon.HTTP_200
        data = json.loads(result.text)
        assert data["last_filling"] is None
        assert data["remaining"] == 0
        assert data["history"] == []

    def test_history_with_data(self, client: falcon.testing.TestClient):
        """Test history after filling and watering."""
        client.simulate_get("/watering.api/fill/2000")
        client.simulate_get("/watering.api/water/250")

        result = client.simulate_get("/watering.api/history")

        assert result.status == falcon.HTTP_200
        data = json.loads(result.text)
        assert data["last_filling"]["quantity"] == 2000
        assert data["remaining"] == 1750
        assert len(data["history"]) == 1


class TestCORS:
    """Tests for CORS middleware."""

    def test_cors_header(self, client: falcon.testing.TestClient):
        """Test CORS headers are set."""
        result = client.simulate_get(
            "/watering.api/history",
            headers={"Origin": "http://localhost:3000"},
        )

        assert result.status == falcon.HTTP_200
        assert "Access-Control-Allow-Origin" in result.headers
