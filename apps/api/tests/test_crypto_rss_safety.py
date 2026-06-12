import pytest

from monitor_api.scanners import CryptoRssSignalAdapter

RSS_FIXTURE = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <item>
      <title>Solidity Protocol Engineer</title>
      <link>https://example.org/jobs/solidity</link>
      <guid>solidity-engineer</guid>
      <description>Write smart contracts and backend integrations.</description>
    </item>
    <item>
      <title>Community Manager</title>
      <link>https://example.org/jobs/community</link>
      <guid>community-manager</guid>
      <description>Manage Discord and social channels.</description>
    </item>
  </channel>
</rss>
"""


def test_crypto_rss_adapter_filters_with_non_allowlisted_query_terms():
    adapter = CryptoRssSignalAdapter(
        feed_url="https://example.org/rss.xml",
        fetch_feed=lambda _url: RSS_FIXTURE,
    )

    signals = adapter.scan(query="solidity engineer", limit=10)

    assert [signal.source_id for signal in signals] == ["solidity-engineer"]


def test_default_crypto_rss_fetch_rejects_non_http_urls():
    adapter = CryptoRssSignalAdapter(feed_url="file:///tmp/secret-feed.xml")

    with pytest.raises(ValueError, match="Only http and https RSS feed URLs are allowed"):
        adapter.scan(query="python", limit=1)
