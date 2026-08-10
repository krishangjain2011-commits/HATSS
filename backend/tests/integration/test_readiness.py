"""Database-backed integration test for the readiness endpoint."""

import os

import pytest
from fastapi.testclient import TestClient

from app.main import app

pytestmark = pytest.mark.skipif(
    os.getenv("HATSS_RUN_DATABASE_TESTS") != "true",
    reason="Set HATSS_RUN_DATABASE_TESTS=true with PostgreSQL configured.",
)


def test_readiness_endpoint_reports_database_availability() -> None:
    """Readiness must prove that the API can connect to PostgreSQL."""
    client = TestClient(app)

    response = client.get("/api/v1/health/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "available"}
