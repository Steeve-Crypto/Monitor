from __future__ import annotations

import hashlib
import json

from monitor_api.models import (
    ActionKind,
    ActionProposal,
    ContactRoute,
    ModelProvenance,
    Opportunity,
    OutreachDraft,
    Profile,
    RiskLevel,
)

PROMPT_VERSION = "deterministic-tailor-v1"
MODEL_PROVIDER = "local"
MODEL_NAME = "deterministic-template"


def create_outreach_draft(
    opportunity: Opportunity,
    profile: Profile | None = None,
) -> OutreachDraft:
    display_name = profile.display_name if profile is not None else "the operator"
    skills = ", ".join(opportunity.required_skills[:5]) or "Python, automation, and web3 delivery"
    subject = f"Re: {opportunity.title}"
    body = (
        f"Hi — I can help with {opportunity.title}.\n\n"
        f"I am {display_name}, focused on {skills}. "
        "Your post looks aligned with practical Python/web3 delivery: "
        f"{opportunity.description}\n\n"
        "Proposed next step: confirm scope, success criteria, timeline, "
        "and access constraints before any implementation."
    )
    payload = {
        "opportunity_id": opportunity.id,
        "subject": subject,
        "body": body,
        "template_family": "technical-fit-v1",
    }
    return OutreachDraft(
        opportunity_id=opportunity.id,
        platform=opportunity.source_platform,
        contact_route=opportunity.contact_route,
        template_family="technical-fit-v1",
        subject=subject,
        body=body,
        payload_hash=payload_hash(payload),
        model_provenance=ModelProvenance(
            provider=MODEL_PROVIDER,
            model=MODEL_NAME,
            prompt_version=PROMPT_VERSION,
        ),
    )


def create_action_proposal(opportunity: Opportunity, draft: OutreachDraft) -> ActionProposal:
    action_kind = _action_kind_for_contact_route(opportunity.contact_route)
    risk_level = RiskLevel.MEDIUM if action_kind != ActionKind.LOCAL_SCAN else RiskLevel.LOW
    payload_preview = {
        "opportunity_id": opportunity.id,
        "draft_id": draft.id,
        "template_family": draft.template_family,
        "subject": draft.subject,
        "body": draft.body,
    }
    proposal = ActionProposal(
        action_kind=action_kind,
        platform=opportunity.source_platform,
        destination=str(opportunity.source_url or opportunity.source_id),
        payload_preview=payload_preview,
        payload_hash=payload_hash(payload_preview),
        risk_level=risk_level,
        match_score=opportunity.qualification_score,
        scam_risk_score=opportunity.scam_risk_score,
        bid_amount=opportunity.budget_min,
        currency=opportunity.currency,
        requires_approval=True,
    )
    return proposal


def payload_hash(payload: dict) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()


def _action_kind_for_contact_route(contact_route: ContactRoute) -> ActionKind:
    if contact_route is ContactRoute.EMAIL:
        return ActionKind.EMAIL_SEND
    if contact_route is ContactRoute.DIRECT_MESSAGE:
        return ActionKind.DM_SEND
    if contact_route in {ContactRoute.PLATFORM_PROPOSAL, ContactRoute.APPLICATION_FORM}:
        return ActionKind.PROPOSAL_SUBMIT
    return ActionKind.DRAFT_CREATE
