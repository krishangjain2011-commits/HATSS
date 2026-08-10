"""Contract tests for live Windows network telemetry."""

from fastapi.testclient import TestClient

from app.main import app


def test_network_overview_reports_source_state() -> None:
    response = TestClient(app).get("/api/v1/network/overview")

    assert response.status_code == 200
    body = response.json()
    assert body["source"] == "windows_networking"
    assert body["state"]["status"] in {"available", "unavailable"}
