from fastapi.testclient import TestClient

from monitor_api.app import create_app
from monitor_api.scanners import CryptoRssSignalAdapter, SignalMeshScanner

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


def test_scan_source_endpoint_rejects_unconfigured_sources_without_fake_data(tmp_path):
    client = TestClient(create_app(storage_path=tmp_path / "signal_mesh.json"))

    response = client.post(
        "/api/scans/x/run",
        json={"query": "need python web3 dashboard", "limit": 2},
    )

    assert response.status_code == 503
    assert "Signal source is not configured: x" in response.json()["detail"]
    assert client.get("/api/signals").json()["count"] == 0


def test_scan_source_endpoint_captures_configured_crypto_rss_signals_in_store(tmp_path):
    scanner = SignalMeshScanner(
        adapters={
            "crypto_rss": CryptoRssSignalAdapter(
                feed_url="https://example.org/feed.xml",
                fetch_feed=lambda _url: RSS_FIXTURE,
            )
        }
    )
    client = TestClient(create_app(storage_path=tmp_path / "signal_mesh.json", scanner=scanner))

    response = client.post(
        "/api/scans/crypto_rss/run",
        json={"query": "python web3", "limit": 2},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["source"] == "crypto_rss"
    assert body["count"] == 1
    assert body["items"][0]["source_platform"] == "rss"

    list_response = client.get("/api/signals")
    assert list_response.json()["count"] == 1


def test_scan_source_endpoint_rejects_unknown_source(tmp_path):
    client = TestClient(create_app(storage_path=tmp_path / "signal_mesh.json"))

    response = client.post(
        "/api/scans/linkedin/run",
        json={"query": "python", "limit": 1},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Unsupported signal source: linkedin"
