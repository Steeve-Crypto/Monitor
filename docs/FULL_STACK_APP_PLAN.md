# Monitor Full-Stack App Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Build Monitor as a local-first full-stack command deck that scrapes/monitors authorized X, Discord, marketplace, and crypto job-board sources for project signals and paid gigs; filters for Python, AI automation, and web3 work; drafts personalized proposals/DMs/emails with local LLM or Grok; and executes approved or policy-authorized applications/outreach with full auditability.

**Architecture:** A desktop-first full-stack app: Tauri shell + SvelteKit frontend + Three.js visualization layer, backed by a local Python FastAPI service for vault, signal scanners, marketplace adapters, Hermes skill orchestration, risk/autopilot policy enforcement, and audit logging. The app is offline-capable for private data, stores sensitive data locally, and uses explicit risk classification plus scoped autopilot policies to decide whether an action needs human approval or can execute automatically.

**Tech Stack:** Tauri, SvelteKit, TypeScript, Three.js, Python 3.12, FastAPI, Pydantic v2, SQLModel/SQLAlchemy, SQLite/PostgreSQL, vector index (sqlite-vss/LanceDB/Qdrant local), cryptography, keyring, Playwright for whitelisted workflows, X API + Grok API, Discord bot/API, RSS/email ingestion, Ollama, Hermes Agent.

---

## 1. Product / UX Stance

Monitor is not a terminal-first tool. The primary experience is a dark premium full-stack command deck. CLI commands are utility surfaces for automation, debugging, and recovery, not the main product.

The core action is: detect high-signal buying intent, transform signals into ranked actionable missions, prepare tailored proposals/DMs/emails, and execute when either the operator approves or the action matches a scoped autopilot policy.

## 2. Approval Policy

Human-in-the-loop is mandatory by default for reputation-risk actions:

- Submitting applications, proposals, bids, or outreach under the operator's identity on Upwork, Fiverr, crypto job boards, X, Discord, or email.
- Creating, modifying, or deleting accounts/profile data on external platforms.
- Sending messages to recruiters, clients, hiring managers, or public threads.
- Uploading resumes, portfolios, credentials, or sensitive identity artifacts.
- Any browser automation on a platform marked medium/high risk.

Scoped autopilot may bypass per-action approval only when all of these match:

- Platform/account/channel is explicitly whitelisted.
- Opportunity category is approved, e.g. Python automation, FastAPI/backend, web3 dashboards, bots, smart-contract integrations.
- Minimum match score and maximum scam-risk thresholds are met.
- Proposal template family is approved.
- Daily send/bid limits and cooldowns are enforced.
- Bid/budget bounds are respected.
- Payload hash, model provenance, and policy ID are logged.
- Kill switch is available from Mission Control.

Human approval is not required for low-risk internal operations:

- Fetching public job listings from APIs/RSS/public pages.
- Normalizing and deduplicating opportunities.
- Local ranking, scoring, Python/web3 qualification, drafting, and simulation.
- Local dashboard updates, metrics, and reflection over stored outcomes.
- Preparing drafts that are not transmitted externally.

Every action still receives a risk classification, model provenance, policy decision, and audit record.

## 3. Information Architecture

### Primary Navigation

1. Mission Control
   - Daily opportunity intake, system status, priority recommendations.
2. Signal Mesh
   - X/Discord/project signals, marketplace leads, crypto job posts, source health, dedupe, ranked opportunity cards.
3. Opportunity Detail
   - Original posting, match score, compensation signal, requirements, risk notes.
4. Tailoring Studio
   - Resume slices, cover letter/proposal drafts, prompt trace, local/API routing indicator.
5. Approval Cockpit
   - Only appears for reputation-risk actions. Shows exact payload, destination, identity used, risk level, policy notes, and approve/edit/reject/defer actions.
6. Vault
   - Profile sections, credentials, portfolio refs, platform whitelist, backup/export.
7. Automation Console
   - Scanner schedules, X/Grok searches, Discord watched channels, marketplace adapters, Playwright sessions, Hermes skill runs, autopilot policies.
8. Metrics & Reflection
   - Applications, responses, interviews, wins, skill evolution history.
9. Settings
   - Models, Hermes runtime, local/API routing, risk thresholds, themes.

## 4. Core Screens

### Mission Control

Purpose: Give the operator a live cockpit for what matters now.

Sections:
- Today’s priority opportunities.
- Scanner health and last run timestamps for X, Discord, marketplaces, crypto boards, RSS/email.
- Drafts waiting for review.
- Reputation-risk queue and autopilot activity feed.
- Outcome reminders.

Actions:
- Start scan or run targeted X/Discord/marketplace hunt.
- Open top opportunity.
- Review approval queue.
- Run reflection.

### Signal Mesh / Opportunity Mesh

Purpose: Browse and triage all discovered opportunities.

Components:
- Holographic table/grid cards.
- Filters: source, location, remote, compensation, match score, risk, status.
- Deduped opportunity clusters.
- Source reliability badges.
- Buyer intent, scam risk, budget quality, Python/web3 fit, and urgency indicators.

Actions:
- Save, reject, defer, send to tailoring, inspect source, queue DM/proposal, add source query.

### Tailoring Studio

Purpose: Create high-quality proposals, bids, DMs, emails, and resume slices before any external action.

Components:
- Posting pane.
- Profile context pane.
- Generated artifacts pane for Upwork proposals, Fiverr replies, X DMs/replies, Discord DMs/messages, crypto board applications, and email outreach.
- Diff view: base vs tailored resume/proposal.
- Sensitivity indicator: local-only/API-safe.

Actions:
- Generate draft.
- Regenerate section.
- Edit manually.
- Send to Approval Cockpit if reputation-risk and no autopilot policy matches.
- Send via scoped autopilot if policy matches and limits allow.

### Approval Cockpit

Purpose: Prevent reputation damage while keeping low-risk automation fast.

Components:
- Exact outbound payload preview.
- Destination/account/platform details.
- Identity and credential scope used.
- Risk classification and reason.
- Platform policy notes.
- Audit log preview.

Actions:
- Approve once.
- Edit and approve.
- Reject.
- Defer.
- Mark platform/account as higher risk.

### Vault

Purpose: Manage sensitive identity data locally.

Components:
- Unlock state.
- Profile sections.
- Credentials.
- Portfolio refs.
- Whitelisted platforms.
- Encrypted backup/export controls.

Actions:
- Unlock/lock.
- Add/update profile data.
- Add credential.
- Rotate/export backup.

## 5. Backend Domains

### Vault Service

Responsibilities:
- Encrypted profile and credential storage.
- Keyring/master-password flows.
- In-memory unlock sessions.
- Redaction before LLM calls.

### Signal & Opportunity Service

Responsibilities:
- X/Grok query adapters for public posts and buying-intent discovery.
- Discord bot/API adapters for approved servers/channels.
- Marketplace adapters for Upwork, Fiverr, and other freelance sources through APIs, alerts, or whitelisted workflows.
- Crypto board adapters for Web3.career, CryptoJobsList, Cryptocurrency Jobs, Remote3, Dework/Gitcoin-style bounties.
- Normalization, dedupe, semantic memory, and source health tracking.
- Python/web3 qualification and match/ranking inputs.

### Hermes Orchestration Service

Responsibilities:
- Invoke Scout, Tailor, Executor, Reflector skills.
- Track skill versions and runs.
- Enforce local/API routing by sensitivity.

### Risk, Approval & Autopilot Policy Service

Responsibilities:
- Classify every proposed action as low/medium/high reputation risk.
- Require approval for reputation-risk actions by default.
- Evaluate scoped autopilot policies for trusted sends/submissions.
- Enforce rate limits, budget limits, template constraints, platform/channel whitelists, cooldowns, and kill switch.
- Persist approval decisions, policy decisions, payload hashes, and model provenance.

### Audit Service

Responsibilities:
- Immutable event log.
- Queryable timeline.
- Evidence trail for external actions and skill evolution.

## 6. Frontend Data Contracts

Initial API routes:

- `GET /api/health`
- `POST /api/vault/unlock`
- `POST /api/vault/lock`
- `GET /api/profile`
- `PUT /api/profile`
- `GET /api/signals`
- `GET /api/opportunities`
- `POST /api/scans/run`
- `POST /api/scans/x/run`
- `POST /api/scans/discord/run`
- `POST /api/scans/marketplaces/run`
- `POST /api/scans/crypto/run`
- `POST /api/opportunities/{id}/qualify`
- `POST /api/opportunities/{id}/rank`
- `POST /api/opportunities/{id}/tailor`
- `POST /api/actions/propose`
- `POST /api/actions/{id}/approve`
- `POST /api/actions/{id}/reject`
- `GET /api/autopilot/policies`
- `POST /api/autopilot/policies`
- `POST /api/autopilot/kill-switch`
- `GET /api/audit`
- `POST /api/reflection/run`

Every proposed external action returns:

```json
{
  "action_id": "act_...",
  "risk_level": "low|medium|high",
  "requires_approval": true,
  "autopilot_policy_id": null,
  "risk_reasons": [],
  "destination": {},
  "payload_preview": {},
  "payload_hash": "sha256...",
  "model_provenance": {"provider": "ollama|grok|other", "model": "..."}
}
```

## 7. Implementation Phases

### Phase A — Full-Stack Foundation

- Create monorepo structure: `apps/desktop`, `apps/api`, `packages/shared`.
- Add Tauri + frontend shell.
- Add Python FastAPI service.
- Define shared API contracts.
- Add health check wiring from UI to backend.

### Phase B — Vault + Profile

- Implement encrypted vault.
- Build Vault screen and profile editor.
- Add unlock/lock state to UI.
- Verify no plaintext secrets are written to disk.

### Phase C — Signal Mesh & Opportunity Ingestion

- Implement source adapter interface.
- Add X/Grok public signal adapter.
- Add Discord approved-channel adapter.
- Add Upwork/Fiverr alert or whitelisted workflow adapter.
- Add crypto job board adapters.
- Normalize ProjectSignal and Opportunity objects with Pydantic.
- Add dedupe and semantic memory.
- Build Signal Mesh / Opportunity Mesh UI.

### Phase D — Qualification & Tailoring Studio

- Add Hermes Scout/Qualifier/Tailor orchestration.
- Add local model vs Grok routing flags.
- Build proposal/DM/email generation and diff UI.
- Add scam-risk, buyer-intent, budget-quality, and Python/web3-fit scoring.

### Phase E — Risk-Based Approval Cockpit + Scoped Autopilot

- Implement risk classifier.
- Gate reputation-risk actions by default.
- Implement scoped autopilot policies for pre-authorized sends/submissions.
- Build approval queue, cockpit, autopilot activity feed, and kill switch.
- Add immutable audit events.

### Phase F — Execution + Reflection

- Implement whitelisted execution adapters.
- Add Reflector runs and skill evolution history.
- Add metrics dashboard.

## 8. Verification Gates

Each phase must prove:

- App launches locally.
- Frontend can reach backend.
- Sensitive data remains encrypted at rest.
- Low-risk actions can run without approval.
- Reputation-risk actions cannot execute without approval unless a matching scoped autopilot policy exists.
- Autopilot enforces platform/channel whitelist, send limits, cooldowns, budget bounds, match threshold, and kill switch.
- Audit log records all material actions.
- Hermes skill calls are traceable and versioned.

## 9. Design Direction

Visual language:
- Deep black / near-black base.
- Purple and cool grey accents.
- Holographic cards, thin neon borders, subtle glow.
- Dense but readable operator-grade layouts.
- Three.js opportunity constellation for discovery/ranking views.

Avoid:
- Bright SaaS minimalism.
- Terminal-first framing.
- Generic admin dashboard feel.
- Approval modals for low-risk internal tasks.

## 10. Sketching Plan

Before production UI, create 2–3 disposable HTML prototypes:

1. Mission Control + Opportunity Mesh variant.
2. Tailoring Studio + Approval Cockpit variant.
3. Vault + Metrics/Reflection variant.

Pick the strongest direction, then implement in the Tauri full-stack app.
