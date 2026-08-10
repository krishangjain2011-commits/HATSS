"""Contract tests for live, read-only host telemetry."""

from fastapi.testclient import TestClient

from app.main import app
from app.services.system_monitor import _windows_edition_label


def test_system_overview_returns_live_telemetry_contract() -> None:
    response = TestClient(app).get("/api/v1/system/overview")

    assert response.status_code == 200
    body = response.json()
    assert body["data_mode"] == "live"
    assert body["source"] == "native"
    assert body["host"]["hostname"]
    assert 0 <= body["cpu"]["usage_percent"] <= 100
    assert 0 <= body["memory"]["usage_percent"] <= 100
    assert body["running_processes"] >= len(body["top_processes"])
    assert body["process_collection_status"] in {"available", "limited"}


def test_windows_11_builds_are_not_labeled_as_windows_10() -> None:
    assert _windows_edition_label("Windows 10 Pro", 26100) == "Windows 11 Pro"
    assert _windows_edition_label("Windows 10 Pro", 19045) == "Windows 10 Pro"
