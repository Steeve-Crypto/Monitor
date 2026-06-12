from fastapi.testclient import TestClient

from monitor_api.app import create_app


def test_health_endpoint_reports_monitor_api_ready():
    client = TestClient(create_app())

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {
        "service": "monitor-api",
        "status": "ok",
        "version": "0.1.0",
    }


def test_list_signals_starts_empty_and_uses_contract_shape():
    client = TestClient(create_app())

    response = client.get("/api/signals")

    assert response.status_code == 200
    body = response.json()
    assert body == {"items": [], "count": 0}


def test_create_signal_returns_normalized_project_signal():
    client = TestClient(create_app())

    response = client.post(
        "/api/signals",
        json={
            "source_platform": "x",
            "source_id": "tweet-123",
            "source_url": "https://x.com/founder/status/123",
            "title": "Need Python automation help",
            "raw_text": "Looking for a Python dev to automate a crypto dashboard this week.",
            "signal_kind": "buying_intent",
            "detected_keywords": ["python", "automation", "crypto"],
            "contact_route": "public_reply",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["id"].startswith("sig_")
    assert body["source_platform"] == "x"
    assert body["status"] == "new"
    assert body["risk_level"] == "low"

    list_response = client.get("/api/signals")
    assert list_response.json()["count"] == 1


def test_list_opportunities_starts_empty_and_uses_contract_shape():
    client = TestClient(create_app())

    response = client.get("/api/opportunities")

    assert response.status_code == 200
    assert response.json() == {"items": [], "count": 0}


def test_create_opportunity_returns_qualification_fields():
    client = TestClient(create_app())

    response = client.post(
        "/api/opportunities",
        json={
            "source_platform": "upwork",
            "source_id": "job-1",
            "title": "Build FastAPI wallet analytics dashboard",
            "description": "Need Python/FastAPI backend and web3 wallet analytics dashboard.",
            "required_skills": ["python", "fastapi", "web3"],
            "budget_min": 1500,
            "budget_max": 3000,
            "currency": "USD",
            "contact_route": "platform_proposal",
            "python_fit_score": 0.95,
            "web3_fit_score": 0.85,
            "buyer_intent_score": 0.9,
            "scam_risk_score": 0.05,
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["id"].startswith("opp_")
    assert body["qualification_score"] >= 0.85
    assert body["is_target_fit"] is True
