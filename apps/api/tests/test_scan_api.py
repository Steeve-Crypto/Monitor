from fastapi.testclient import TestClient

from monitor_api.app import create_app


def test_scan_source_endpoint_captures_x_signals_in_store(tmp_path):
    client = TestClient(create_app(storage_path=tmp_path / "signal_mesh.json"))

    response = client.post(
        "/api/scans/x/run",
        json={"query": "need python web3 dashboard", "limit": 2},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["source"] == "x"
    assert body["count"] == 2
    assert body["items"][0]["source_platform"] == "x"

    list_response = client.get("/api/signals")
    assert list_response.json()["count"] == 2


def test_scan_source_endpoint_supports_discord_marketplaces_and_crypto(tmp_path):
    client = TestClient(create_app(storage_path=tmp_path / "signal_mesh.json"))

    for source in ["discord", "marketplaces", "crypto"]:
        response = client.post(
            f"/api/scans/{source}/run",
            json={"query": "python automation", "limit": 1},
        )
        assert response.status_code == 200
        assert response.json()["source"] == source
        assert response.json()["count"] == 1

    assert client.get("/api/signals").json()["count"] == 3


def test_scan_source_endpoint_rejects_unknown_source(tmp_path):
    client = TestClient(create_app(storage_path=tmp_path / "signal_mesh.json"))

    response = client.post(
        "/api/scans/linkedin/run",
        json={"query": "python", "limit": 1},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Unsupported signal source: linkedin"
