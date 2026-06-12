from fastapi.testclient import TestClient

from monitor_api.app import create_app
from monitor_api.models import Platform, ProjectSignal
from monitor_api.qualification import qualify_opportunity, score_signal
from monitor_api.store import JsonSignalMeshStore


def test_scores_high_fit_python_web3_lead():
    signal = ProjectSignal(
        source_platform=Platform.UPWORK,
        source_id="job-high-fit",
        title="Need Python FastAPI web3 wallet analytics dashboard ASAP",
        raw_text=(
            "Hiring an experienced Python/FastAPI developer to build a web3 wallet "
            "analytics dashboard. Budget is $2500, paid contract, start this week."
        ),
        detected_keywords=["python", "fastapi", "web3"],
        budget_hint="$2500",
        contact_route="platform_proposal",
    )

    scores = score_signal(signal)

    assert scores.python_fit_score >= 0.8
    assert scores.web3_fit_score >= 0.8
    assert scores.buyer_intent_score >= 0.8
    assert scores.urgency_score >= 0.6
    assert scores.budget_quality_score >= 0.7
    assert scores.response_likelihood_score >= 0.6
    assert scores.scam_risk_score <= 0.2


def test_scores_low_fit_lead():
    signal = ProjectSignal(
        source_platform=Platform.X,
        source_id="post-low-fit",
        title="Looking for logo ideas",
        raw_text="Maybe someday I will need a designer for a logo. No budget yet, just browsing.",
    )

    opportunity = qualify_opportunity(signal)

    assert opportunity.python_fit_score <= 0.2
    assert opportunity.web3_fit_score <= 0.2
    assert opportunity.buyer_intent_score <= 0.4
    assert opportunity.budget_quality_score <= 0.2
    assert opportunity.qualification_score < 0.4
    assert opportunity.is_target_fit is False


def test_scores_scam_risk_language():
    signal = ProjectSignal(
        source_platform=Platform.DISCORD,
        source_id="dm-risky",
        title="Guaranteed crypto profit if you pay first",
        raw_text=(
            "Urgent guaranteed 10x crypto opportunity. Send seed phrase and pay upfront "
            "verification fee before we release funds."
        ),
        contact_route="direct_message",
    )

    scores = score_signal(signal)

    assert scores.scam_risk_score >= 0.8


def test_convert_signal_to_opportunity_persists_scores_and_is_idempotent(tmp_path):
    store = JsonSignalMeshStore(tmp_path / "signal_mesh.json")
    signal = store.add_signal(
        ProjectSignal(
            source_platform=Platform.UPWORK,
            source_id="job-convert",
            title="Build Python web3 automation",
            raw_text="Need a Python developer for web3 automation. Budget $1200, start today.",
            contact_route="platform_proposal",
        )
    )
    client = TestClient(create_app(store=store))

    first_response = client.post(f"/api/signals/{signal.id}/qualify")
    second_response = client.post(f"/api/signals/{signal.id}/qualify")

    assert first_response.status_code == 201
    assert second_response.status_code == 200
    first_body = first_response.json()
    second_body = second_response.json()
    assert first_body["id"] == second_body["id"]
    assert first_body["source_signal_id"] == signal.id
    assert first_body["python_fit_score"] >= 0.7
    assert first_body["web3_fit_score"] >= 0.7
    assert client.get("/api/opportunities").json()["count"] == 1


def test_convert_signal_to_opportunity_404s_when_signal_missing(tmp_path):
    client = TestClient(create_app(storage_path=tmp_path / "signal_mesh.json"))

    response = client.post("/api/signals/sig_missing/qualify")

    assert response.status_code == 404
