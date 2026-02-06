"""Tests for the FastAPI application."""

import pytest
from fastapi.testclient import TestClient

from watering.app import create_app
from watering.config import Config, get_config
from watering.hardware import WateringController
from watering.routes import get_controller


@pytest.fixture
def client(config: Config, watering_controller: WateringController):
    """Create test client for the application."""
    app = create_app(config, use_mock_gpio=True)

    # Override dependencies with test instances
    app.dependency_overrides[get_config] = lambda: config
    app.dependency_overrides[get_controller] = lambda: watering_controller

    with TestClient(app) as client:
        yield client


class TestWateringEndpoint:
    """Tests for watering endpoint."""

    def test_water_success(self, client: TestClient):
        """Test successful watering request."""
        response = client.get("/watering.api/water/250")

        assert response.status_code == 200
        data = response.json()
        assert data["action"] == "water"
        assert data["volume"] == 250
        assert "duration" in data

    def test_water_invalid_volume(self, client: TestClient):
        """Test watering with invalid volume."""
        response = client.get("/watering.api/water/abc")

        assert response.status_code == 422  # FastAPI validation error

    def test_water_negative_volume(self, client: TestClient):
        """Test watering with negative volume."""
        response = client.get("/watering.api/water/-100")

        assert response.status_code == 422  # FastAPI validation error

    def test_water_zero_volume(self, client: TestClient):
        """Test watering with zero volume."""
        response = client.get("/watering.api/water/0")

        assert response.status_code == 422  # FastAPI validation error


class TestFillingEndpoint:
    """Tests for filling endpoint."""

    def test_fill_success(self, client: TestClient):
        """Test successful filling request."""
        response = client.get("/watering.api/fill/2000")

        assert response.status_code == 200
        data = response.json()
        assert data["action"] == "record_filling"
        assert data["volume"] == 2000

    def test_fill_invalid_volume(self, client: TestClient):
        """Test filling with invalid volume."""
        response = client.get("/watering.api/fill/xyz")

        assert response.status_code == 422  # FastAPI validation error

    def test_fill_zero_volume(self, client: TestClient):
        """Test filling with zero volume."""
        response = client.get("/watering.api/fill/0")

        assert response.status_code == 422  # FastAPI validation error


class TestHistoryEndpoint:
    """Tests for history endpoint."""

    def test_history_empty(self, client: TestClient):
        """Test history with no data."""
        response = client.get("/watering.api/history")

        assert response.status_code == 200
        data = response.json()
        assert data["last_filling"] is None
        assert data["remaining"] == 0
        assert data["history"] == []

    def test_history_with_data(self, client: TestClient):
        """Test history after filling and watering."""
        client.get("/watering.api/fill/2000")
        client.get("/watering.api/water/250")

        response = client.get("/watering.api/history")

        assert response.status_code == 200
        data = response.json()
        assert data["last_filling"]["quantity"] == 2000
        assert data["remaining"] == 1750
        assert len(data["history"]) == 1


class TestCORS:
    """Tests for CORS middleware."""

    def test_cors_header(self, client: TestClient):
        """Test CORS headers are set."""
        response = client.get(
            "/watering.api/history",
            headers={"Origin": "http://localhost:3000"},
        )

        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers


class TestOpenAPI:
    """Tests for OpenAPI documentation."""

    def test_openapi_available(self, client: TestClient):
        """Test OpenAPI schema is available."""
        response = client.get("/openapi.json")

        assert response.status_code == 200
        data = response.json()
        assert data["info"]["title"] == "Watering API"
        assert "/watering.api/water/{volume}" in data["paths"]

    def test_docs_available(self, client: TestClient):
        """Test Swagger docs are available."""
        response = client.get("/docs")

        assert response.status_code == 200
