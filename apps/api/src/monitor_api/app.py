from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, Header, HTTPException, Response, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from monitor_api import __version__
from monitor_api.executor import (
    EXECUTOR_WEBHOOK_URL_ENV,
    DisabledExternalExecutor,
    ExternalExecutor,
    ExternalExecutorError,
    ExternalExecutorNotConfiguredError,
    WebhookExternalExecutor,
)
from monitor_api.models import (
    ActionProposal,
    Application,
    ApprovalDecision,
    ApprovalStatus,
    AuditEvent,
    Opportunity,
    OutreachDraft,
    Profile,
    ProjectSignal,
)
from monitor_api.profile_vault import ProfileVault, VaultPasswordError
from monitor_api.qualification import mark_signal_qualified, qualify_opportunity
from monitor_api.scanners import (
    SignalMeshScanner,
    SourceNotConfiguredError,
    UnsupportedSignalSourceError,
)
from monitor_api.store import JsonSignalMeshStore, SignalMeshStore
from monitor_api.tailor import create_action_proposal, create_outreach_draft


class HealthResponse(BaseModel):
    service: str
    status: str
    version: str


class ProjectSignalListResponse(BaseModel):
    items: list[ProjectSignal]
    count: int


class OpportunityListResponse(BaseModel):
    items: list[Opportunity]
    count: int


class OutreachDraftListResponse(BaseModel):
    items: list[OutreachDraft]
    count: int


class ActionProposalListResponse(BaseModel):
    items: list[ActionProposal]
    count: int


class ApprovalDecisionListResponse(BaseModel):
    items: list[ApprovalDecision]
    count: int


class AuditEventListResponse(BaseModel):
    items: list[AuditEvent]
    count: int


class ApplicationListResponse(BaseModel):
    items: list[Application]
    count: int


class ProfileListResponse(BaseModel):
    items: list[Profile]
    count: int


class ScanRequest(BaseModel):
    query: str
    limit: int = 10


class ScanResponse(BaseModel):
    source: str
    items: list[ProjectSignal]
    count: int


class StoreStatsResponse(BaseModel):
    signals_count: int
    opportunities_count: int
    drafts_count: int = 0
    action_proposals_count: int = 0
    audit_events_count: int = 0
    applications_count: int = 0
    storage_path: str
    storage_exists: bool


class DraftRequest(BaseModel):
    profile_id: str | None = None


class ActionProposalRequest(BaseModel):
    draft_id: str | None = None


class ApprovalDecisionRequest(BaseModel):
    decided_by: str = "operator"
    notes: str | None = None


def create_app(
    store: SignalMeshStore | None = None,
    storage_path: str | Path | None = None,
    vault_path: str | Path | None = None,
    scanner: SignalMeshScanner | None = None,
    executor: ExternalExecutor | None = None,
) -> FastAPI:
    if store is not None and storage_path is not None:
        raise ValueError("Pass either store or storage_path, not both.")

    app = FastAPI(
        title="Monitor API",
        version=__version__,
        description=(
            "Local API for Monitor signal discovery, qualification, "
            "and risk/autopilot contracts."
        ),
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://127.0.0.1:5173",
            "http://localhost:5173",
            "http://127.0.0.1:4173",
            "http://localhost:4173",
        ],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    signal_store = store if store is not None else JsonSignalMeshStore(storage_path)
    profile_vault = ProfileVault(vault_path)
    signal_scanner = scanner if scanner is not None else SignalMeshScanner.with_default_adapters()
    if executor is not None:
        external_executor = executor
    elif os.getenv(EXECUTOR_WEBHOOK_URL_ENV):
        external_executor = WebhookExternalExecutor()
    else:
        external_executor = DisabledExternalExecutor()

    def require_vault_password(password: str | None) -> str:
        if not password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="X-Vault-Password header is required.",
            )
        return password

    def vault_error_to_http(exc: VaultPasswordError) -> HTTPException:
        detail = str(exc)
        if "required" in detail.lower():
            return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)
        return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)

    def find_opportunity(opportunity_id: str) -> Opportunity:
        for opportunity in signal_store.list_opportunities():
            if opportunity.id == opportunity_id:
                return opportunity
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Opportunity not found: {opportunity_id}",
        )

    def find_draft(draft_id: str) -> OutreachDraft | None:
        for draft in signal_store.list_outreach_drafts():
            if draft.id == draft_id:
                return draft
        return None

    def record_audit(event_type: str, entity_id: str, metadata: dict | None = None) -> AuditEvent:
        event = AuditEvent(
            event_type=event_type,
            actor="monitor-api",
            entity_id=entity_id,
            metadata=metadata or {},
        )
        return signal_store.add_audit_event(event)

    @app.get("/api/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        return HealthResponse(service="monitor-api", status="ok", version=__version__)

    @app.get("/api/signals", response_model=ProjectSignalListResponse)
    def list_signals() -> ProjectSignalListResponse:
        signals = signal_store.list_signals()
        return ProjectSignalListResponse(items=signals, count=len(signals))

    @app.post(
        "/api/signals",
        response_model=ProjectSignal,
        status_code=status.HTTP_201_CREATED,
    )
    def create_signal(signal: ProjectSignal) -> ProjectSignal:
        return signal_store.add_signal(signal)

    @app.post(
        "/api/signals/{signal_id}/qualify",
        response_model=Opportunity,
        status_code=status.HTTP_201_CREATED,
    )
    def qualify_signal(signal_id: str, response: Response) -> Opportunity:
        signal = signal_store.get_signal(signal_id)
        if signal is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Signal not found: {signal_id}",
            )

        existing = signal_store.get_opportunity_by_source_signal_id(signal_id)
        if existing is not None:
            response.status_code = status.HTTP_200_OK
            return existing

        opportunity = qualify_opportunity(signal)
        saved = signal_store.add_opportunity(opportunity)
        signal_store.update_signal(mark_signal_qualified(signal))
        return saved

    @app.post("/api/scans/{source}/run", response_model=ScanResponse)
    def run_scan(source: str, request: ScanRequest) -> ScanResponse:
        try:
            signals = signal_scanner.scan_source(source, query=request.query, limit=request.limit)
        except UnsupportedSignalSourceError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
        except SourceNotConfiguredError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=str(exc),
            ) from exc
        new_signals = signal_store.add_signals(signals)
        return ScanResponse(source=source, items=new_signals, count=len(new_signals))

    @app.get("/api/store/stats", response_model=StoreStatsResponse)
    def store_stats() -> StoreStatsResponse:
        return StoreStatsResponse.model_validate(signal_store.stats())

    @app.get("/api/opportunities", response_model=OpportunityListResponse)
    def list_opportunities() -> OpportunityListResponse:
        opportunities = signal_store.list_opportunities()
        return OpportunityListResponse(items=opportunities, count=len(opportunities))

    @app.post(
        "/api/opportunities",
        response_model=Opportunity,
        status_code=status.HTTP_201_CREATED,
    )
    def create_opportunity(opportunity: Opportunity) -> Opportunity:
        return signal_store.add_opportunity(opportunity)

    @app.post(
        "/api/opportunities/{opportunity_id}/draft",
        response_model=OutreachDraft,
        status_code=status.HTTP_201_CREATED,
    )
    def create_draft(
        opportunity_id: str,
        request: DraftRequest,
        x_vault_password: str | None = Header(default=None),
    ) -> OutreachDraft:
        opportunity = find_opportunity(opportunity_id)
        profile = None
        if request.profile_id is not None:
            password = require_vault_password(x_vault_password)
            try:
                profile = profile_vault.get_profile(request.profile_id, password)
            except VaultPasswordError as exc:
                raise vault_error_to_http(exc) from exc
            if profile is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Profile not found: {request.profile_id}",
                )
        draft = signal_store.add_outreach_draft(create_outreach_draft(opportunity, profile))
        record_audit(
            "outreach_draft.created",
            draft.id,
            {"opportunity_id": opportunity.id, "profile_id": request.profile_id},
        )
        return draft

    @app.get("/api/outreach-drafts", response_model=OutreachDraftListResponse)
    def list_drafts() -> OutreachDraftListResponse:
        drafts = signal_store.list_outreach_drafts()
        return OutreachDraftListResponse(items=drafts, count=len(drafts))

    @app.post(
        "/api/opportunities/{opportunity_id}/actions/propose",
        response_model=ActionProposal,
        status_code=status.HTTP_201_CREATED,
    )
    def propose_action(
        opportunity_id: str,
        request: ActionProposalRequest,
    ) -> ActionProposal:
        opportunity = find_opportunity(opportunity_id)
        draft = find_draft(request.draft_id) if request.draft_id else None
        if request.draft_id is not None and draft is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Outreach draft not found: {request.draft_id}",
            )
        if draft is None:
            draft = signal_store.add_outreach_draft(create_outreach_draft(opportunity))
            record_audit(
                "outreach_draft.created",
                draft.id,
                {"opportunity_id": opportunity.id, "profile_id": None},
            )
        proposal = signal_store.add_action_proposal(create_action_proposal(opportunity, draft))
        record_audit(
            "action_proposal.created",
            proposal.id,
            {"opportunity_id": opportunity.id, "draft_id": draft.id},
        )
        return proposal

    @app.get("/api/actions/proposals", response_model=ActionProposalListResponse)
    def list_action_proposals() -> ActionProposalListResponse:
        proposals = signal_store.list_action_proposals()
        return ActionProposalListResponse(items=proposals, count=len(proposals))

    @app.post(
        "/api/actions/{action_id}/approve",
        response_model=ApprovalDecision,
        status_code=status.HTTP_201_CREATED,
    )
    def approve_action(action_id: str, request: ApprovalDecisionRequest) -> ApprovalDecision:
        if signal_store.get_action_proposal(action_id) is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Action proposal not found: {action_id}",
            )
        decision = signal_store.add_approval_decision(
            ApprovalDecision(
                action_proposal_id=action_id,
                status=ApprovalStatus.APPROVED,
                decided_by=request.decided_by,
                notes=request.notes,
            )
        )
        record_audit(
            "approval_decision.approved",
            decision.id,
            {"action_proposal_id": action_id},
        )
        return decision

    @app.post(
        "/api/actions/{action_id}/reject",
        response_model=ApprovalDecision,
        status_code=status.HTTP_201_CREATED,
    )
    def reject_action(action_id: str, request: ApprovalDecisionRequest) -> ApprovalDecision:
        if signal_store.get_action_proposal(action_id) is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Action proposal not found: {action_id}",
            )
        decision = signal_store.add_approval_decision(
            ApprovalDecision(
                action_proposal_id=action_id,
                status=ApprovalStatus.REJECTED,
                decided_by=request.decided_by,
                notes=request.notes,
            )
        )
        record_audit(
            "approval_decision.rejected",
            decision.id,
            {"action_proposal_id": action_id},
        )
        return decision

    @app.get("/api/actions/decisions", response_model=ApprovalDecisionListResponse)
    def list_approval_decisions() -> ApprovalDecisionListResponse:
        decisions = signal_store.list_approval_decisions()
        return ApprovalDecisionListResponse(items=decisions, count=len(decisions))

    @app.post("/api/actions/{action_id}/execute", response_model=Application)
    def execute_action(action_id: str) -> Application:
        proposal = signal_store.get_action_proposal(action_id)
        if proposal is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Action proposal not found: {action_id}",
            )
        approved = any(
            decision.action_proposal_id == action_id and decision.status == ApprovalStatus.APPROVED
            for decision in signal_store.list_approval_decisions()
        )
        if proposal.requires_approval and not approved:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Action proposal requires approval before execution.",
            )
        try:
            application = external_executor.execute(proposal)
        except ExternalExecutorNotConfiguredError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=str(exc),
            ) from exc
        except ExternalExecutorError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=str(exc),
            ) from exc
        saved = signal_store.add_application(application)
        record_audit(
            "external_action.executed",
            saved.id,
            {"action_proposal_id": action_id, "application_status": saved.status.value},
        )
        return saved

    @app.get("/api/applications", response_model=ApplicationListResponse)
    def list_applications() -> ApplicationListResponse:
        applications = signal_store.list_applications()
        return ApplicationListResponse(items=applications, count=len(applications))

    @app.get("/api/audit", response_model=AuditEventListResponse)
    def list_audit_events() -> AuditEventListResponse:
        events = signal_store.list_audit_events()
        return AuditEventListResponse(items=events, count=len(events))

    @app.get("/api/profiles", response_model=ProfileListResponse)
    def list_profiles(x_vault_password: str | None = Header(default=None)) -> ProfileListResponse:
        password = require_vault_password(x_vault_password)
        try:
            profiles = profile_vault.list_profiles(password)
        except VaultPasswordError as exc:
            raise vault_error_to_http(exc) from exc
        return ProfileListResponse(items=profiles, count=len(profiles))

    @app.post(
        "/api/profiles",
        response_model=Profile,
        status_code=status.HTTP_201_CREATED,
    )
    def create_profile(
        profile: Profile,
        x_vault_password: str | None = Header(default=None),
    ) -> Profile:
        password = require_vault_password(x_vault_password)
        try:
            return profile_vault.add_profile(profile, password)
        except VaultPasswordError as exc:
            raise vault_error_to_http(exc) from exc

    @app.get("/api/profiles/{profile_id}", response_model=Profile)
    def get_profile(
        profile_id: str,
        x_vault_password: str | None = Header(default=None),
    ) -> Profile:
        password = require_vault_password(x_vault_password)
        try:
            profile = profile_vault.get_profile(profile_id, password)
        except VaultPasswordError as exc:
            raise vault_error_to_http(exc) from exc
        if profile is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Profile not found: {profile_id}",
            )
        return profile

    return app


app = create_app()
