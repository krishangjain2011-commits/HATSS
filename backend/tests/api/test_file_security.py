"""Contracts for explicit Defender custom scan endpoints."""

from fastapi.testclient import TestClient

from app.main import app


def test_file_security_capability_reports_source_state() -> None:
    response = TestClient(app).get("/api/v1/file-security/defender")

    assert response.status_code == 200
    assert response.json()["source"] == "microsoft_defender"


def test_file_security_rejects_relative_scan_directories() -> None:
    response = TestClient(app).post(
        "/api/v1/file-security/defender/scans", json={"directory": "Downloads"}
    )

    assert response.status_code == 422
