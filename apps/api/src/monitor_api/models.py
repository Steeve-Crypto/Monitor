from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, computed_field, field_validator


def _prefixed_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


class Platform(StrEnum):
    X = "x"
    DISCORD = "discord"
    UPWORK = "upwork"
    FIVERR = "fiverr"
    WEB3_CAREER = "web3_career"
    CRYPTOJOBS_LIST = "cryptojobs_list"
    CRYPTOCURRENCY_JOBS = "cryptocurrency_jobs"
    REMOTE3 = "remote3"
    DEWORK = "dework"
    GITCOIN = "gitcoin"
    EMAIL = "email"
    RSS = "rss"
    GITHUB = "github"
    OTHER = "other"


class RiskLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ContactRoute(StrEnum):
    NONE = "none"
    PUBLIC_REPLY = "public_reply"
    DIRECT_MESSAGE = "direct_message"
    PLATFORM_PROPOSAL = "platform_proposal"
    EMAIL = "email"
    APPLICATION_FORM = "application_form"
    DISCORD_CHANNEL = "discord_channel"


class SignalKind(StrEnum):
    BUYING_INTENT = "buying_intent"
    HIRING = "hiring"
    BOUNTY = "bounty"
    GRANT = "grant"
    PROJECT_LAUNCH = "project_launch"
    REFERRAL_REQUEST = "referral_request"
    OTHER = "other"


class SignalStatus(StrEnum):
    NEW = "new"
    QUALIFIED = "qualified"
    REJECTED = "rejected"
    CONVERTED = "converted"


class OpportunityStatus(StrEnum):
    NEW = "new"
    QUALIFIED = "qualified"
    DRAFTED = "drafted"
    APPLIED = "applied"
    REJECTED = "rejected"
    WON = "won"
    LOST = "lost"


class ApplicationStatus(StrEnum):
    DRAFTED = "drafted"
    PENDING_APPROVAL = "pending_approval"
    SUBMITTED = "submitted"
    RESPONDED = "responded"
    WON = "won"
    LOST = "lost"


class ActionKind(StrEnum):
    LOCAL_SCAN = "local_scan"
    QUALIFY = "qualify"
    DRAFT_CREATE = "draft_create"
    PROPOSAL_SUBMIT = "proposal_submit"
    DM_SEND = "dm_send"
    EMAIL_SEND = "email_send"
    BID_SUBMIT = "bid_submit"
    PROFILE_UPDATE = "profile_update"
    CREDENTIAL_USE = "credential_use"


class ApprovalStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    DEFERRED = "deferred"


class MonitorBaseModel(BaseModel):
    model_config = ConfigDict(use_enum_values=False, validate_assignment=True)


class ModelProvenance(MonitorBaseModel):
    provider: str = Field(..., min_length=1, examples=["ollama", "grok"])
    model: str = Field(..., min_length=1)
    prompt_version: str | None = None
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class Profile(MonitorBaseModel):
    id: str = Field(default_factory=lambda: _prefixed_id("prof"))
    display_name: str
    target_roles: list[str] = Field(default_factory=list)
    target_skills: list[str] = Field(default_factory=lambda: ["python", "web3", "automation"])
    preferred_platforms: list[Platform] = Field(default_factory=list)
    max_daily_autopilot_sends: int = Field(default=0, ge=0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ProjectSignal(MonitorBaseModel):
    id: str = Field(default_factory=lambda: _prefixed_id("sig"))
    source_platform: Platform
    source_id: str
    source_url: HttpUrl | None = None
    title: str = Field(..., min_length=1)
    raw_text: str = Field(..., min_length=1)
    signal_kind: SignalKind = SignalKind.OTHER
    status: SignalStatus = SignalStatus.NEW
    detected_keywords: list[str] = Field(default_factory=list)
    project_name: str | None = None
    budget_hint: str | None = None
    contact_route: ContactRoute = ContactRoute.NONE
    risk_level: RiskLevel = RiskLevel.LOW
    captured_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class Opportunity(MonitorBaseModel):
    id: str = Field(default_factory=lambda: _prefixed_id("opp"))
    source_signal_id: str | None = None
    source_platform: Platform
    source_id: str
    source_url: HttpUrl | None = None
    title: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    required_skills: list[str] = Field(default_factory=list)
    budget_min: float | None = Field(default=None, ge=0)
    budget_max: float | None = Field(default=None, ge=0)
    currency: str = "USD"
    contact_route: ContactRoute = ContactRoute.NONE
    status: OpportunityStatus = OpportunityStatus.NEW
    python_fit_score: float = Field(default=0.0, ge=0.0, le=1.0)
    web3_fit_score: float = Field(default=0.0, ge=0.0, le=1.0)
    buyer_intent_score: float = Field(default=0.0, ge=0.0, le=1.0)
    budget_quality_score: float = Field(default=0.0, ge=0.0, le=1.0)
    urgency_score: float = Field(default=0.0, ge=0.0, le=1.0)
    response_likelihood_score: float = Field(default=0.0, ge=0.0, le=1.0)
    scam_risk_score: float = Field(default=0.0, ge=0.0, le=1.0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @field_validator("currency")
    @classmethod
    def normalize_currency(cls, value: str) -> str:
        return value.upper()

    @computed_field
    @property
    def qualification_score(self) -> float:
        stack_fit = max(self.python_fit_score, self.web3_fit_score)
        context_quality = max(
            self.budget_quality_score,
            self.urgency_score,
            self.response_likelihood_score,
        )
        positive = stack_fit * 0.60 + self.buyer_intent_score * 0.35 + context_quality * 0.05
        penalty = self.scam_risk_score * 0.25
        return round(max(0.0, min(1.0, positive - penalty)), 4)

    @computed_field
    @property
    def is_target_fit(self) -> bool:
        return self.python_fit_score >= 0.7 or self.web3_fit_score >= 0.7


class OutreachDraft(MonitorBaseModel):
    id: str = Field(default_factory=lambda: _prefixed_id("draft"))
    opportunity_id: str
    platform: Platform
    contact_route: ContactRoute
    template_family: str
    subject: str | None = None
    body: str = Field(..., min_length=1)
    payload_hash: str = Field(..., min_length=1)
    model_provenance: ModelProvenance
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class Application(MonitorBaseModel):
    id: str = Field(default_factory=lambda: _prefixed_id("app"))
    opportunity_id: str
    outreach_draft_id: str | None = None
    action_proposal_id: str | None = None
    status: ApplicationStatus = ApplicationStatus.DRAFTED
    submitted_at: datetime | None = None
    outcome_notes: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class Skill(MonitorBaseModel):
    id: str = Field(default_factory=lambda: _prefixed_id("skill"))
    name: str
    version: str = "0.1.0"
    purpose: str
    source_path: str | None = None
    enabled: bool = True
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ActionProposal(MonitorBaseModel):
    id: str = Field(default_factory=lambda: _prefixed_id("act"))
    action_kind: ActionKind
    platform: Platform
    destination: str
    payload_preview: dict = Field(default_factory=dict)
    payload_hash: str = Field(..., min_length=1)
    risk_level: RiskLevel = RiskLevel.LOW
    match_score: float = Field(default=0.0, ge=0.0, le=1.0)
    scam_risk_score: float = Field(default=0.0, ge=0.0, le=1.0)
    bid_amount: float | None = Field(default=None, ge=0)
    currency: str = "USD"
    requires_approval: bool = False
    autopilot_policy_id: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @field_validator("currency")
    @classmethod
    def normalize_action_currency(cls, value: str) -> str:
        return value.upper()

    def evaluate_policy(self, policies: list[AutopilotPolicy]) -> None:
        self.autopilot_policy_id = None
        self.requires_approval = self.risk_level in {RiskLevel.MEDIUM, RiskLevel.HIGH}
        for policy in policies:
            if policy.allows(self):
                self.autopilot_policy_id = policy.id
                self.requires_approval = False
                return


class AutopilotPolicy(MonitorBaseModel):
    id: str = Field(default_factory=lambda: _prefixed_id("pol"))
    name: str
    enabled: bool = False
    platforms: list[Platform] = Field(default_factory=list)
    allowed_action_kinds: list[ActionKind] = Field(default_factory=list)
    approved_template_families: list[str] = Field(default_factory=list)
    max_sends_per_day: int = Field(default=0, ge=0)
    min_match_score: float = Field(default=0.0, ge=0.0, le=1.0)
    max_scam_risk_score: float = Field(default=0.2, ge=0.0, le=1.0)
    max_bid_amount: float | None = Field(default=None, ge=0)
    currency: str = "USD"
    cooldown_seconds: int = Field(default=0, ge=0)
    kill_switch_engaged: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @field_validator("currency")
    @classmethod
    def normalize_policy_currency(cls, value: str) -> str:
        return value.upper()

    def allows(self, proposal: ActionProposal) -> bool:
        if not self.enabled or self.kill_switch_engaged:
            return False
        if proposal.platform not in self.platforms:
            return False
        if proposal.action_kind not in self.allowed_action_kinds:
            return False
        if proposal.match_score < self.min_match_score:
            return False
        if proposal.scam_risk_score > self.max_scam_risk_score:
            return False
        if proposal.bid_amount is not None and self.max_bid_amount is not None:
            if proposal.currency != self.currency or proposal.bid_amount > self.max_bid_amount:
                return False
        template_family = proposal.payload_preview.get("template_family")
        if (
            self.approved_template_families
            and template_family not in self.approved_template_families
        ):
            return False
        return True


class ApprovalDecision(MonitorBaseModel):
    id: str = Field(default_factory=lambda: _prefixed_id("appr"))
    action_proposal_id: str
    status: ApprovalStatus = ApprovalStatus.PENDING
    decided_by: str
    notes: str | None = None
    decided_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class AuditEvent(MonitorBaseModel):
    id: str = Field(default_factory=lambda: _prefixed_id("evt"))
    event_type: str
    actor: str
    entity_id: str
    metadata: dict = Field(default_factory=dict)
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
