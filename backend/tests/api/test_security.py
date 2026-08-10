"""Contracts for real Windows-security data source endpoints."""

from datetime import UTC, datetime

from fastapi.testclient import TestClient

from app.main import app
from app.schemas.file_security import DefenderScanAction


def test_defender_endpoint_reports_source_state() -> None:
    response = TestClient(app).get("/api/v1/security/defender")

    assert response.status_code == 200
    body = response.json()
    assert body["source"] == "microsoft_defender"
    assert body["state"]["status"] in {"available", "unavailable"}


def test_sysmon_endpoint_reports_source_state() -> None:
    response = TestClient(app).get("/api/v1/security/sysmon")

    assert response.status_code == 200
    body = response.json()
    assert body["source"] == "sysmon"
    assert body["state"]["status"] in {"available", "unavailable"}


def test_defender_scan_capability_endpoint_reports_source_state() -> None:
    response = TestClient(app).get("/api/v1/file-security/defender")

    assert response.status_code == 200
    body = response.json()
    assert body["source"] == "microsoft_defender"
    assert body["state"]["status"] in {"available", "unavailable"}


def test_defender_scan_rejects_a_blank_directory() -> None:
    response = TestClient(app).post("/api/v1/file-security/defender/scans", json={"directory": " "})

    assert response.status_code == 422


def test_defender_scan_endpoint_returns_explicit_start_state(monkeypatch) -> None:
    def start_scan(directory: str) -> DefenderScanAction:
        return DefenderScanAction(
            state="started",
            directory=directory,
            detail="Microsoft Defender accepted the requested custom scan.",
            requested_at=datetime.now(UTC),
        )

    monkeypatch.setattr("app.api.v1.endpoints.file_security.start_defender_custom_scan", start_scan)
    response = TestClient(app).post(
        "/api/v1/file-security/defender/scans", json={"directory": r"C:\\Users\\demo\\Downloads"}
    )

    assert response.status_code == 202
    assert response.json()["state"] == "started"
