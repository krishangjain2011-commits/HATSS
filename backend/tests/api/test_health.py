"""Tests for infrastructure-only HTTP endpoints."""

from fastapi.testclient import TestClient

from app.main import app


def test_liveness_endpoint_reports_api_metadata() -> None:
    """The API must remain observable even when PostgreSQL is unavailable."""
    client = TestClient(app)

    response = client.get("/api/v1/health/live")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "hatss-api",
        "version": "0.1.0",
    }
