import pytest

from monitor_api.models import ContactRoute, Platform, SignalKind, SignalStatus
from monitor_api.scanners import (
    DiscordSignalAdapter,
    MarketplaceSignalAdapter,
    MockSignalAdapter,
    SignalMeshScanner,
    UnsupportedSignalSourceError,
    XSignalAdapter,
)


def test_mock_adapter_converts_query_into_project_signal():
    adapter = MockSignalAdapter(
        platform=Platform.X,
        signal_kind=SignalKind.BUYING_INTENT,
        contact_route=ContactRoute.PUBLIC_REPLY,
    )

    signals = adapter.scan(query="python web3 dashboard", limit=2)

    assert len(signals) == 2
    assert signals[0].source_platform is Platform.X
    assert signals[0].signal_kind is SignalKind.BUYING_INTENT
    assert signals[0].status is SignalStatus.NEW
    assert "python" in signals[0].detected_keywords
    assert "web3" in signals[0].detected_keywords


def test_signal_mesh_scanner_registers_default_x_discord_marketplace_crypto_adapters():
    scanner = SignalMeshScanner.with_default_adapters()

    assert isinstance(scanner.get_adapter("x"), XSignalAdapter)
    assert isinstance(scanner.get_adapter("discord"), DiscordSignalAdapter)
    assert isinstance(scanner.get_adapter("marketplaces"), MarketplaceSignalAdapter)
    assert scanner.get_adapter("crypto").platform is Platform.WEB3_CAREER


def test_signal_mesh_scanner_runs_source_and_limits_results():
    scanner = SignalMeshScanner.with_default_adapters()

    signals = scanner.scan_source("x", query="need python bot", limit=1)

    assert len(signals) == 1
    assert signals[0].source_platform is Platform.X
    assert signals[0].contact_route is ContactRoute.PUBLIC_REPLY
    assert signals[0].risk_level.value == "low"


def test_signal_mesh_scanner_rejects_unknown_source():
    scanner = SignalMeshScanner.with_default_adapters()

    with pytest.raises(UnsupportedSignalSourceError):
        scanner.scan_source("linkedin", query="python", limit=1)
