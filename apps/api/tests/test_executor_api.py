from fastapi.testclient import TestClient

from monitor_api.app import create_app
from monitor_api.executor import ExternalExecutor
from monitor_api.models import Application, ApplicationStatus, ContactRoute, Opportunity, Platform


class RecordingExecutor(ExternalExecutor):
    def __init__(self):
        self.executed = []

    def execute(self, proposal):
        self.executed.append(proposal.id)
        return Application(
            opportunity_id=proposal.payload_preview["opportunity_id"],
            action_proposal_id=proposal.id,
            status=ApplicationStatus.SUBMITTED,
            outcome_notes="Recorded by injected test executor.",
        )


def _client_with_proposal(tmp_path, executor=None):
    client = TestClient(
        create_app(
            storage_path=tmp_path / "store.json",
            vault_path=tmp_path / "vault.json",
            executor=executor,
        )
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
    opportunity_id = client.post(
        "/api/opportunities",
        json=opportunity.model_dump(mode="json"),
    ).json()["id"]
    proposal = client.post(f"/api/opportunities/{opportunity_id}/actions/propose", json={}).json()
    return client, proposal


def test_execute_action_requires_approval_before_external_send(tmp_path):
    executor = RecordingExecutor()
    client, proposal = _client_with_proposal(tmp_path, executor=executor)

    response = client.post(f"/api/actions/{proposal['id']}/execute")

    assert response.status_code == 409
    assert "requires approval" in response.json()["detail"]
    assert executor.executed == []


def test_execute_action_uses_real_configured_executor_after_approval(tmp_path):
    executor = RecordingExecutor()
    client, proposal = _client_with_proposal(tmp_path, executor=executor)
    client.post(f"/api/actions/{proposal['id']}/approve", json={"decided_by": "operator"})

    response = client.post(f"/api/actions/{proposal['id']}/execute")

    assert response.status_code == 200
    application = response.json()
    assert application["status"] == "submitted"
    assert application["action_proposal_id"] == proposal["id"]
    assert executor.executed == [proposal["id"]]
    assert client.get("/api/applications").json()["count"] == 1
    event_types = [event["event_type"] for event in client.get("/api/audit").json()["items"]]
    assert "external_action.executed" in event_types


def test_execute_action_returns_503_when_no_executor_is_configured(tmp_path):
    client, proposal = _client_with_proposal(tmp_path)
    client.post(f"/api/actions/{proposal['id']}/approve", json={"decided_by": "operator"})

    response = client.post(f"/api/actions/{proposal['id']}/execute")

    assert response.status_code == 503
    assert "External executor is not configured" in response.json()["detail"]
