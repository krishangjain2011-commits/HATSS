"""Contracts for the intentionally disabled-by-default local copilot."""

from fastapi.testclient import TestClient

from app.main import app


def test_copilot_status_is_explicit_when_not_enabled(monkeypatch) -> None:
    monkeypatch.setenv("HATSS_COPILOT_ENABLED", "false")
    from app.core.config import get_settings

    get_settings.cache_clear()
    response = TestClient(app).get("/api/v1/copilot/status")

    assert response.status_code == 200
    assert response.json()["provider"] == "ollama"
    assert response.json()["enabled"] is False


def test_copilot_brief_requires_a_configured_provider(monkeypatch) -> None:
    monkeypatch.setenv("HATSS_COPILOT_ENABLED", "false")
    from app.core.config import get_settings

    get_settings.cache_clear()
    response = TestClient(app).post(
        "/api/v1/copilot/brief",
        json={"question": "Summarize current evidence.", "confirm_local_evidence": True},
    )

    assert response.status_code == 503
