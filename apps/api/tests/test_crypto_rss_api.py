from fastapi.testclient import TestClient

from monitor_api.app import create_app
from monitor_api.scanners import CryptoRssSignalAdapter, SignalMeshScanner

RSS_FIXTURE = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <item>
      <title>Python Web3 API Contractor</title>
      <link>https://example.org/jobs/python-web3-api</link>
      <guid>api-contractor</guid>
      <description>Short contract building FastAPI services for a crypto data product.</description>
    </item>
  </channel>
</rss>
"""


def test_crypto_rss_scan_endpoint_persists_only_new_feed_items(tmp_path):
    scanner = SignalMeshScanner(
        adapters={
            "crypto_rss": CryptoRssSignalAdapter(
                feed_url="https://example.org/rss.xml",
                fetch_feed=lambda _url: RSS_FIXTURE,
            )
        }
    )
    client = TestClient(create_app(storage_path=tmp_path / "signal_mesh.json", scanner=scanner))

    first_response = client.post(
        "/api/scans/crypto_rss/run",
        json={"query": "python web3", "limit": 10},
    )
    second_response = client.post(
        "/api/scans/crypto_rss/run",
        json={"query": "python web3", "limit": 10},
    )

    assert first_response.status_code == 200
    assert first_response.json()["count"] == 1
    assert second_response.status_code == 200
    assert second_response.json()["count"] == 0
    assert client.get("/api/signals").json()["count"] == 1
