import pytest

from monitor_api.models import Platform
from monitor_api.scanners import (
    CryptoRssSignalAdapter,
    DiscordSignalAdapter,
    MarketplaceSignalAdapter,
    SignalMeshScanner,
    SourceNotConfiguredError,
    UnsupportedSignalSourceError,
    XSignalAdapter,
)

RSS_FIXTURE = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <item>
      <title>Python Web3 Builder</title>
      <link>https://example.org/jobs/python-web3</link>
      <guid>python-web3-builder</guid>
      <description>Paid FastAPI dashboard work for a crypto analytics team.</description>
    </item>
  </channel>
</rss>
"""


def test_default_adapters_do_not_generate_fake_signals_for_unconfigured_sources():
    scanner = SignalMeshScanner.with_default_adapters()

    with pytest.raises(SourceNotConfiguredError):
        scanner.scan_source("x", query="need python bot", limit=1)


def test_signal_mesh_scanner_registers_default_source_contracts_without_fake_data():
    scanner = SignalMeshScanner.with_default_adapters()

    assert isinstance(scanner.get_adapter("x"), XSignalAdapter)
    assert isinstance(scanner.get_adapter("discord"), DiscordSignalAdapter)
    assert isinstance(scanner.get_adapter("marketplaces"), MarketplaceSignalAdapter)
    assert scanner.get_adapter("crypto").platform is Platform.WEB3_CAREER
    assert scanner.get_adapter("crypto_rss").platform is Platform.RSS


def test_signal_mesh_scanner_runs_configured_crypto_rss_source():
    scanner = SignalMeshScanner.with_default_adapters(
        crypto_rss_feed_url="https://example.org/feed.xml",
        crypto_rss_fetcher=lambda _url: RSS_FIXTURE,
    )

    signals = scanner.scan_source("crypto_rss", query="python web3", limit=1)

    assert len(signals) == 1
    assert signals[0].source_platform is Platform.RSS
    assert signals[0].source_id == "python-web3-builder"


def test_crypto_rss_requires_real_configuration_before_scanning():
    adapter = CryptoRssSignalAdapter()

    with pytest.raises(SourceNotConfiguredError):
        adapter.scan(query="python", limit=1)


def test_signal_mesh_scanner_rejects_unknown_source():
    scanner = SignalMeshScanner.with_default_adapters()

    with pytest.raises(UnsupportedSignalSourceError):
        scanner.scan_source("linkedin", query="python", limit=1)
