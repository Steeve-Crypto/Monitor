from fastapi.testclient import TestClient

from monitor_api.app import create_app
from monitor_api.models import ContactRoute, Opportunity, Platform, Profile


def _client_with_opportunity(tmp_path):
    client = TestClient(
        create_app(storage_path=tmp_path / "store.json", vault_path=tmp_path / "vault.json")
    )
    opportunity = Opportunity(
        source_platform=Platform.RSS,
        source_id="real-job-1",
        title="Python Web3 Backend Engineer",
        description="Paid FastAPI and data pipeline work for a crypto analytics dashboard.",
        required_skills=["python", "fastapi", "web3"],
        contact_route=ContactRoute.APPLICATION_FORM,
        python_fit_score=1.0,
        web3_fit_score=1.0,
        buyer_intent_score=0.9,
        scam_risk_score=0.03,
    )
    created = client.post("/api/opportunities", json=opportunity.model_dump(mode="json"))
    assert created.status_code == 201
    return client, created.json()


def test_create_outreach_draft_for_opportunity_without_external_execution(tmp_path):
    client, opportunity = _client_with_opportunity(tmp_path)

    response = client.post(f"/api/opportunities/{opportunity['id']}/draft", json={})

    assert response.status_code == 201
    draft = response.json()
    assert draft["opportunity_id"] == opportunity["id"]
    assert draft["model_provenance"]["provider"] == "local"
    assert draft["model_provenance"]["model"] == "deterministic-template"
    assert draft["payload_hash"]
    assert "Python Web3 Backend Engineer" in draft["body"]

    stats = client.get("/api/store/stats").json()
    assert stats["drafts_count"] == 1
    assert stats["action_proposals_count"] == 0


def test_create_draft_with_profile_requires_vault_password_and_uses_encrypted_profile(tmp_path):
    client, opportunity = _client_with_opportunity(tmp_path)
    profile = Profile(display_name="Steeve", target_skills=["python", "web3"])
    created_profile = client.post(
        "/api/profiles",
        headers={"X-Vault-Password": "secret"},
        json=profile.model_dump(mode="json"),
    ).json()

    missing_password = client.post(
        f"/api/opportunities/{opportunity['id']}/draft",
        json={"profile_id": created_profile["id"]},
    )
    assert missing_password.status_code == 401

    response = client.post(
        f"/api/opportunities/{opportunity['id']}/draft",
        headers={"X-Vault-Password": "secret"},
        json={"profile_id": created_profile["id"]},
    )
    assert response.status_code == 201
    assert "Steeve" in response.json()["body"]
    assert "Steeve" not in (tmp_path / "vault.json").read_text()


def test_action_proposal_requires_approval_and_does_not_execute(tmp_path):
    client, opportunity = _client_with_opportunity(tmp_path)
    draft = client.post(f"/api/opportunities/{opportunity['id']}/draft", json={}).json()

    response = client.post(
        f"/api/opportunities/{opportunity['id']}/actions/propose",
        json={"draft_id": draft["id"]},
    )

    assert response.status_code == 201
    proposal = response.json()
    assert proposal["requires_approval"] is True
    assert proposal["risk_level"] == "medium"
    assert proposal["payload_preview"]["draft_id"] == draft["id"]

    proposals = client.get("/api/actions/proposals").json()
    assert proposals["count"] == 1
    assert proposals["items"][0]["id"] == proposal["id"]


def test_approval_decisions_are_recorded_without_external_execution(tmp_path):
    client, opportunity = _client_with_opportunity(tmp_path)
    proposal = client.post(
        f"/api/opportunities/{opportunity['id']}/actions/propose",
        json={},
    ).json()

    approved = client.post(
        f"/api/actions/{proposal['id']}/approve",
        json={"decided_by": "operator", "notes": "Looks accurate"},
    )

    assert approved.status_code == 201
    assert approved.json()["status"] == "approved"
    assert approved.json()["action_proposal_id"] == proposal["id"]

    rejected = client.post(
        f"/api/actions/{proposal['id']}/reject",
        json={"decided_by": "operator", "notes": "Testing rejection log"},
    )
    assert rejected.status_code == 201
    assert rejected.json()["status"] == "rejected"


def test_audit_log_records_draft_proposal_and_decisions(tmp_path):
    client, opportunity = _client_with_opportunity(tmp_path)
    draft = client.post(f"/api/opportunities/{opportunity['id']}/draft", json={}).json()
    proposal = client.post(
        f"/api/opportunities/{opportunity['id']}/actions/propose",
        json={"draft_id": draft["id"]},
    ).json()
    client.post(f"/api/actions/{proposal['id']}/approve", json={"decided_by": "operator"})

    audit = client.get("/api/audit")

    assert audit.status_code == 200
    event_types = [event["event_type"] for event in audit.json()["items"]]
    assert event_types == [
        "outreach_draft.created",
        "action_proposal.created",
        "approval_decision.approved",
    ]
    assert audit.json()["count"] == 3
