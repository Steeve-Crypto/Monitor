from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from monitor_api.models import (
    ActionKind,
    ActionProposal,
    Application,
    ApplicationStatus,
    ApprovalDecision,
    ApprovalStatus,
    AuditEvent,
    AutopilotPolicy,
    ContactRoute,
    ModelProvenance,
    Opportunity,
    OpportunityStatus,
    OutreachDraft,
    Platform,
    Profile,
    ProjectSignal,
    RiskLevel,
    SignalKind,
    SignalStatus,
)


def test_project_signal_normalizes_source_and_defaults_to_new_status():
    signal = ProjectSignal(
        source_platform=Platform.X,
        source_id="tweet-123",
        source_url="https://x.com/founder/status/123",
        title="Need Python automation help",
        raw_text="Looking for a Python dev to automate crypto ops dashboard this week.",
        signal_kind=SignalKind.BUYING_INTENT,
        detected_keywords=["python", "automation", "crypto"],
        contact_route=ContactRoute.PUBLIC_REPLY,
    )

    assert signal.status is SignalStatus.NEW
    assert signal.source_platform is Platform.X
    assert signal.detected_keywords == ["python", "automation", "crypto"]
    assert signal.risk_level is RiskLevel.LOW


def test_opportunity_requires_python_or_web3_targeting_signal():
    opportunity = Opportunity(
        source_platform=Platform.UPWORK,
        source_id="job-1",
        title="Build FastAPI wallet analytics dashboard",
        description="Need Python/FastAPI backend and web3 wallet analytics dashboard.",
        required_skills=["python", "fastapi", "web3"],
        budget_min=1500,
        budget_max=3000,
        currency="USD",
        contact_route=ContactRoute.PLATFORM_PROPOSAL,
        python_fit_score=0.95,
        web3_fit_score=0.85,
        buyer_intent_score=0.9,
        scam_risk_score=0.05,
    )

    assert opportunity.status is OpportunityStatus.NEW
    assert opportunity.qualification_score >= 0.85
    assert opportunity.is_target_fit is True


def test_opportunity_rejects_invalid_score_range():
    with pytest.raises(ValidationError):
        Opportunity(
            source_platform=Platform.FIVERR,
            source_id="brief-1",
            title="Invalid score",
            description="Need a bot",
            required_skills=["python"],
            contact_route=ContactRoute.PLATFORM_PROPOSAL,
            python_fit_score=1.5,
        )


def test_autopilot_policy_matches_only_when_constraints_are_satisfied():
    policy = AutopilotPolicy(
        name="Low-risk Upwork Python proposals",
        enabled=True,
        platforms=[Platform.UPWORK],
        allowed_action_kinds=[ActionKind.PROPOSAL_SUBMIT],
        approved_template_families=["python_automation"],
        max_sends_per_day=5,
        min_match_score=0.75,
        max_scam_risk_score=0.2,
        max_bid_amount=2500,
        currency="USD",
    )
    proposal = ActionProposal(
        action_kind=ActionKind.PROPOSAL_SUBMIT,
        platform=Platform.UPWORK,
        destination="upwork://jobs/job-1",
        payload_preview={"bid_amount": 1200, "template_family": "python_automation"},
        payload_hash="sha256:abc123",
        risk_level=RiskLevel.HIGH,
        match_score=0.91,
        scam_risk_score=0.04,
        bid_amount=1200,
        currency="USD",
    )

    assert policy.allows(proposal) is True

    proposal.bid_amount = 3000
    assert policy.allows(proposal) is False


def test_reputation_risk_action_requires_approval_without_matching_policy():
    proposal = ActionProposal(
        action_kind=ActionKind.DM_SEND,
        platform=Platform.X,
        destination="x://user/founder",
        payload_preview={"message": "Short personalized DM"},
        payload_hash="sha256:def456",
        risk_level=RiskLevel.MEDIUM,
        match_score=0.82,
    )

    proposal.evaluate_policy([])

    assert proposal.requires_approval is True
    assert proposal.autopilot_policy_id is None


def test_outreach_draft_tracks_model_provenance_and_payload_hash():
    draft = OutreachDraft(
        opportunity_id="opp_123",
        platform=Platform.DISCORD,
        contact_route=ContactRoute.DIRECT_MESSAGE,
        template_family="web3_dashboard",
        subject="Can help with your dashboard",
        body="Saw your post. I can build this with Python + web3.py quickly.",
        payload_hash="sha256:payload",
        model_provenance=ModelProvenance(provider="ollama", model="qwen2.5"),
    )

    assert draft.model_provenance.provider == "ollama"
    assert draft.template_family == "web3_dashboard"


def test_profile_application_approval_and_audit_event_models_are_serializable():
    now = datetime.now(UTC)
    profile = Profile(display_name="Operator", target_roles=["Python automation", "web3 backend"])
    app = Application(opportunity_id="opp_123", status=ApplicationStatus.DRAFTED)
    decision = ApprovalDecision(
        action_proposal_id="act_123",
        status=ApprovalStatus.APPROVED,
        decided_by="operator",
    )
    event = AuditEvent(
        event_type="approval.created",
        actor="operator",
        entity_id="act_123",
        occurred_at=now,
    )

    assert profile.model_dump()["display_name"] == "Operator"
    assert app.status is ApplicationStatus.DRAFTED
    assert decision.status is ApprovalStatus.APPROVED
    assert event.model_dump()["event_type"] == "approval.created"
