from monitor_api.models import ContactRoute, Platform, SignalKind
from monitor_api.scanners import CryptoRssSignalAdapter, SignalMeshScanner

RSS_FIXTURE = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Crypto Jobs</title>
    <item>
      <title>Senior Python Web3 Data Engineer</title>
      <link>https://example.org/jobs/python-web3-data</link>
      <guid>job-python-web3-data</guid>
      <description>
        Build Python pipelines and dashboards for a DeFi analytics protocol.
      </description>
    </item>
    <item>
      <title>Community Manager</title>
      <link>https://example.org/jobs/community</link>
      <guid>job-community</guid>
      <description>Manage social channels for a crypto project.</description>
    </item>
  </channel>
</rss>
"""


def test_crypto_rss_adapter_parses_feed_and_filters_by_query_keywords():
    adapter = CryptoRssSignalAdapter(
        feed_url="https://example.org/rss.xml",
        fetch_feed=lambda _url: RSS_FIXTURE,
    )

    signals = adapter.scan(query="python web3 dashboard", limit=5)

    assert len(signals) == 1
    signal = signals[0]
    assert signal.source_platform is Platform.RSS
    assert signal.source_id == "job-python-web3-data"
    assert str(signal.source_url) == "https://example.org/jobs/python-web3-data"
    assert signal.title == "Senior Python Web3 Data Engineer"
    assert signal.signal_kind is SignalKind.HIRING
    assert signal.contact_route is ContactRoute.APPLICATION_FORM
    assert signal.detected_keywords == ["python", "web3", "dashboard"]


def test_default_scanner_registers_crypto_rss_adapter_from_feed_url():
    scanner = SignalMeshScanner.with_default_adapters(
        crypto_rss_feed_url="https://example.org/rss.xml",
        crypto_rss_fetcher=lambda _url: RSS_FIXTURE,
    )

    signals = scanner.scan_source("crypto_rss", query="python web3", limit=1)

    assert len(signals) == 1
    assert signals[0].source_id == "job-python-web3-data"
