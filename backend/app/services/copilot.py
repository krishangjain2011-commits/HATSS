"""Explicit, local-only Ollama briefing integration.

The model receives a compact snapshot of available HATSS evidence only after the
caller consents. It cannot execute commands, scan files, change Defender, or
make decisions on behalf of the user.
"""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.core.config import get_settings
from app.schemas.copilot import CopilotBriefResponse, CopilotStatus
from app.services.system_monitor import get_system_overview
from app.services.windows_network import get_network_overview
from app.services.windows_security import get_defender_overview, get_sysmon_overview

logger = logging.getLogger(__name__)


class CopilotUnavailableError(RuntimeError):
    """Raised when a local model is not configured or cannot be reached."""


def _ollama_answer(response_body: bytes) -> str | None:
    """Extract text from Ollama's regular JSON or newline-delimited JSON output."""

    raw_text = response_body.decode("utf-8", errors="replace").strip()
    if not raw_text:
        return None

    try:
        records: list[Any] = [json.loads(raw_text)]
    except json.JSONDecodeError:
        # Ollama normally returns one JSON document when stream=false, but a
        # proxy or older client can still return newline-delimited chunks.
        records = []
        for line in raw_text.splitlines():
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    answer_parts: list[str] = []
    for record in records:
        if not isinstance(record, dict):
            continue
        message = record.get("message")
        if isinstance(message, dict) and isinstance(message.get("content"), str):
            answer_parts.append(message["content"])
        elif isinstance(record.get("response"), str):
            answer_parts.append(record["response"])
    answer = "".join(answer_parts).strip()
    return answer or None


def get_copilot_status() -> CopilotStatus:
    """Describe the configured provider without sending any host evidence."""

    settings = get_settings()
    if not settings.copilot_enabled:
        return CopilotStatus(
            enabled=False,
            model=settings.copilot_model,
            detail="Local AI is disabled. Set HATSS_COPILOT_ENABLED=true after installing Ollama.",
        )
    return CopilotStatus(
        enabled=True,
        model=settings.copilot_model,
        detail=(
            "Local Ollama briefing is configured. The server is checked when you submit; "
            "evidence is sent only after explicit confirmation."
        ),
    )


def _evidence_snapshot() -> dict[str, Any]:
    """Build a bounded snapshot for local analysis after explicit consent."""

    system = get_system_overview()
    defender = get_defender_overview()
    sysmon = get_sysmon_overview()
    network = get_network_overview()
    return {
        "host": {
            "operating_system": system.host.operating_system,
            "uptime_seconds": system.host.uptime_seconds,
            "cpu_usage_percent": system.cpu.usage_percent,
            "memory_usage_percent": system.memory.usage_percent,
            "disk_usage_percent": system.disk.usage_percent,
        },
        "defender": {
            "source_status": defender.state.status,
            "antivirus_enabled": defender.antivirus_enabled,
            "real_time_protection_enabled": defender.real_time_protection_enabled,
            "historical_detection_count": len(defender.detections),
            "detections": [
                {
                    "name": threat.name,
                    "severity": threat.severity,
                    "category": threat.category,
                    "action_success": threat.action_success,
                    "detected_at": threat.detected_at,
                }
                for threat in defender.detections[:20]
            ],
        },
        "sysmon": {
            "source_status": sysmon.state.status,
            "recent_event_count": len(sysmon.events),
            "recent_events": [
                {
                    "event_id": event.event_id,
                    "event_type": event.event_type,
                    "occurred_at": event.occurred_at,
                    "provider": event.provider,
                    # Keep event context useful while bounding prompt size.
                    "message": event.message[:3000],
                }
                for event in sysmon.events[:10]
            ],
        },
        "network": {
            "source_status": network.state.status,
            "neighbor_count": len(network.neighbors),
            "neighbors": [
                {
                    "ip_address": neighbor.ip_address,
                    "state": neighbor.state,
                    "interface": neighbor.interface_alias,
                }
                for neighbor in network.neighbors[:30]
            ],
            "tcp_connection_count": len(network.tcp_connections),
            "tcp_connections": [
                {
                    "local_address": connection.local_address,
                    "local_port": connection.local_port,
                    "remote_address": connection.remote_address,
                    "remote_port": connection.remote_port,
                    "state": connection.state,
                    "process_name": connection.owning_process_name,
                    "process_id": connection.owning_process_id,
                }
                for connection in network.tcp_connections[:50]
            ],
        },
    }


def create_brief(question: str) -> CopilotBriefResponse:
    """Ask the configured local model to explain, not act upon, collected evidence."""

    settings = get_settings()
    if not settings.copilot_enabled:
        raise CopilotUnavailableError("Local AI is disabled in HATSS configuration.")

    evidence = _evidence_snapshot()
    prompt = (
        "You are HATSS, a cyber-safety evidence assistant. "
        "You may explain general cybersecurity terms using your general knowledge. "
        "For questions about this specific computer, use the host, Defender, Sysmon, and "
        "network evidence below. "
        "For each Sysmon event, explain the event type and the important fields in its message "
        "in plain language, then state why it may matter and what it does not prove. "
        "Clearly distinguish observed facts from general explanation and uncertainty. "
        "Do not claim malware, safety, or a threat verdict unless Microsoft Defender explicitly "
        "recorded it. Network connections and event IDs are observations, not proof of malicious "
        "activity; never label an IP, process, or connection malicious without direct evidence. "
        "Do not give commands that alter the host. "
        "If the evidence is unavailable or insufficient, say exactly what is missing and suggest "
        "a safe, human-reviewed next step. "
        "Recommend a human review or an official Defender action when needed.\n\n"
        f"Evidence:\n{json.dumps(evidence, separators=(',', ':'))}\n\nUser question: {question}"
    )
    payload = json.dumps(
        {
            "model": settings.copilot_model,
            "stream": False,
            "messages": [{"role": "user", "content": prompt}],
        }
    ).encode("utf-8")
    request = Request(  # noqa: S310 - local-only URL is validated in application settings
        f"{str(settings.copilot_base_url).rstrip('/')}/api/chat",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(  # noqa: S310 - validated local request
            request, timeout=settings.copilot_timeout_seconds
        ) as response:
            answer = _ollama_answer(response.read())
    except HTTPError as error:
        logger.warning("Ollama rejected the briefing request with HTTP %s", error.code)
        if error.code == 404:
            raise CopilotUnavailableError(
                f"Ollama could not find model '{settings.copilot_model}'. Run ollama pull "
                f"{settings.copilot_model} and try again."
            ) from error
        raise CopilotUnavailableError(
            f"Ollama rejected the briefing request (HTTP {error.code})."
        ) from error
    except TimeoutError as error:
        logger.warning(
            "Ollama briefing timed out after %s seconds", settings.copilot_timeout_seconds
        )
        raise CopilotUnavailableError(
            "Ollama took too long to answer. Try again after the model is loaded."
        ) from error
    except (OSError, URLError) as error:
        logger.warning("Local Ollama request failed: %s", error)
        raise CopilotUnavailableError(
            "Ollama could not be reached. Check that the Ollama app is running."
        ) from error

    if answer is None:
        raise CopilotUnavailableError("Ollama returned no briefing content.")
    return CopilotBriefResponse(
        model=settings.copilot_model,
        generated_at=datetime.now(UTC),
        evidence_sources=[
            "system telemetry",
            "Microsoft Defender",
            "Sysmon",
            "Windows network tables",
        ],
        answer=answer.strip(),
    )
