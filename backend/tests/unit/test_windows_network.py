"""Tests for the Windows network telemetry adapter."""

from app.services import windows_network


def test_network_overview_maps_live_windows_records(monkeypatch) -> None:
    monkeypatch.setattr(windows_network.os, "name", "nt")
    responses = iter(
        [
            {
                "IPAddress": "192.168.1.1",
                "LinkLayerAddress": "00-11-22-33-44-55",
                "State": "Reachable",
                "InterfaceAlias": "Wi-Fi",
                "AddressFamily": "IPv4",
            },
            {
                "LocalAddress": "192.168.1.20",
                "LocalPort": 50123,
                "RemoteAddress": "142.250.195.46",
                "RemotePort": 443,
                "State": "Established",
                "OwningProcess": 1234,
                "OwningProcessName": "msedge",
            },
        ]
    )
    monkeypatch.setattr(windows_network, "_powershell_json", lambda _script: next(responses))

    overview = windows_network.get_network_overview()

    assert overview.state.status == "available"
    assert overview.neighbors[0].ip_address == "192.168.1.1"
    assert overview.tcp_connections[0].owning_process_name == "msedge"


def test_network_overview_is_unavailable_if_a_windows_query_fails(monkeypatch) -> None:
    monkeypatch.setattr(windows_network.os, "name", "nt")
    monkeypatch.setattr(windows_network, "_powershell_json", lambda _script: None)

    overview = windows_network.get_network_overview()

    assert overview.state.status == "unavailable"
    assert not overview.neighbors
    assert not overview.tcp_connections
