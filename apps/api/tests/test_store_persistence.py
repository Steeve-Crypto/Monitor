import json

from fastapi.testclient import TestClient

from monitor_api.app import create_app
from monitor_api.models import Opportunity, Platform, ProjectSignal
from monitor_api.store import JsonSignalMeshStore


def test_json_store_starts_empty_when_file_is_missing(tmp_path):
    storage_path = tmp_path / "signal_mesh.json"

    store = JsonSignalMeshStore(storage_path)

    assert store.list_signals() == []
    assert store.list_opportunities() == []
    assert store.stats()["storage_path"] == str(storage_path)
    assert storage_path.exists() is False


def test_json_store_persists_signals_and_opportunities_between_instances(tmp_path):
    storage_path = tmp_path / "signal_mesh.json"
    first_store = JsonSignalMeshStore(storage_path)
    signal = ProjectSignal(
        source_platform=Platform.X,
        source_id="tweet-123",
        title="Need Python help",
        raw_text="Need Python help with a web3 dashboard.",
    )
    opportunity = Opportunity(
        source_signal_id=signal.id,
        source_platform=Platform.UPWORK,
        source_id="job-123",
        title="Build wallet dashboard",
        description="Need a FastAPI wallet dashboard.",
    )

    first_store.add_signal(signal)
    first_store.add_opportunity(opportunity)
    reloaded_store = JsonSignalMeshStore(storage_path)

    assert [item.id for item in reloaded_store.list_signals()] == [signal.id]
    assert [item.id for item in reloaded_store.list_opportunities()] == [opportunity.id]
    persisted = json.loads(storage_path.read_text())
    assert set(persisted) == {"signals", "opportunities"}
    assert persisted["signals"][0]["captured_at"]
    assert persisted["opportunities"][0]["qualification_score"] >= 0.0


def test_api_persists_created_signal_across_app_instances(tmp_path):
    storage_path = tmp_path / "signal_mesh.json"
    first_client = TestClient(create_app(storage_path=storage_path))

    create_response = first_client.post(
        "/api/signals",
        json={
            "source_platform": "x",
            "source_id": "tweet-abc",
            "title": "Need Python automation",
            "raw_text": "Need Python automation for crypto reporting.",
        },
    )

    assert create_response.status_code == 201
    second_client = TestClient(create_app(storage_path=storage_path))
    list_response = second_client.get("/api/signals")
    assert list_response.status_code == 200
    assert list_response.json()["count"] == 1
    assert list_response.json()["items"][0]["source_id"] == "tweet-abc"


def test_api_persists_created_opportunity_across_app_instances(tmp_path):
    storage_path = tmp_path / "signal_mesh.json"
    first_client = TestClient(create_app(storage_path=storage_path))

    create_response = first_client.post(
        "/api/opportunities",
        json={
            "source_platform": "upwork",
            "source_id": "job-abc",
            "title": "Build FastAPI API",
            "description": "Need a Python FastAPI backend.",
        },
    )

    assert create_response.status_code == 201
    second_client = TestClient(create_app(storage_path=storage_path))
    list_response = second_client.get("/api/opportunities")
    assert list_response.status_code == 200
    assert list_response.json()["count"] == 1
    assert list_response.json()["items"][0]["source_id"] == "job-abc"


def test_scan_endpoint_persists_scanned_signals_across_app_instances(tmp_path):
    storage_path = tmp_path / "signal_mesh.json"
    first_client = TestClient(create_app(storage_path=storage_path))

    scan_response = first_client.post(
        "/api/scans/x/run",
        json={"query": "need python web3 dashboard", "limit": 2},
    )

    assert scan_response.status_code == 200
    second_client = TestClient(create_app(storage_path=storage_path))
    list_response = second_client.get("/api/signals")
    assert list_response.status_code == 200
    assert list_response.json()["count"] == 2
    assert [item["source_platform"] for item in list_response.json()["items"]] == ["x", "x"]


def test_store_stats_endpoint_returns_counts_and_safe_storage_metadata(tmp_path):
    storage_path = tmp_path / "signal_mesh.json"
    client = TestClient(create_app(storage_path=storage_path))
    client.post(
        "/api/scans/discord/run",
        json={"query": "python automation", "limit": 1},
    )

    response = client.get("/api/store/stats")

    assert response.status_code == 200
    body = response.json()
    assert body["signals_count"] == 1
    assert body["opportunities_count"] == 0
    assert body["storage_path"] == str(storage_path)
    assert body["storage_exists"] is True
    assert "secret" not in json.dumps(body).lower()
