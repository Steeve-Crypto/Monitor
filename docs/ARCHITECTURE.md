# Monitor — Architecture

**Status**: Detailed design. Must stay aligned with [SOURCE_OF_TRUTH.md](SOURCE_OF_TRUTH.md).  
**Last Updated**: 2026-06-11  
**Version**: 0.1.0

## 1. System Overview
Monitor is a **Hermes-native, local-first autonomous agent system** for opportunity acquisition. It detects project signals and paid gigs across social/community channels, marketplaces, and crypto job boards; qualifies Python/web3 opportunities; drafts personalized proposals/DMs/emails; and executes approved or pre-authorized actions through a risk-based control layer.

The architecture prioritizes:
- Local sovereignty and encryption
- Hermes self-improving skill loop as the core intelligence
- Risk-based approval gates plus scoped autopilot for pre-authorized reputation-risk actions
- Full-stack dark premium futuristic user experience

## 2. Major Components

### 2.1 Encrypted Identity Vault
- **Location**: Local filesystem (encrypted SQLite or file-based with `cryptography`).
- **Contents**:
  - Structured Profile (JSON): resume text/sections, skills matrix, bio, preferences, DC/remote weighting.
  - Encrypted Credentials store (keyring-backed or master-password encrypted).
  - Portfolio references (local paths + public URLs).
  - Whitelisted Platforms configuration.
- **Access**: Only through Vault Manager module. Never passed raw to LLMs.
- **Backup**: Operator-controlled encrypted exports.

### 2.2 Signal & Opportunity Mesh Scanner
- **Social Signal Layer**: X API/Grok search for buying-intent posts, founder/project hiring signals, web3 bounty mentions, urgent Python automation needs, and DM-worthy threads. Discord bot/API monitors approved servers/channels for gig posts, grant/bounty leads, project launches, and hiring requests.
- **Marketplace Layer**: Upwork, Fiverr, Contra/other freelance marketplaces where available through official interfaces, RSS/email alerts, saved searches, and whitelisted browser workflows.
- **Crypto Job Board Layer**: Cryptocurrency Jobs, CryptoJobsList, Web3.career, Remote3, Dework, Gitcoin bounties/grants, Layer3/Zealy-style bounty surfaces where appropriate.
- **API/RSS/Email Layer**: Company career endpoints, RSS feeds, mailing lists, GitHub issues/discussions, Telegram/Discord forwarded alerts where operator-authorized.
- **Browser Layer**: Playwright only on explicitly whitelisted and compliant workflows. No credential use or submission without approval/autopilot policy.
- **Output**: Normalized `Opportunity` and `ProjectSignal` objects with source, title/post text, project, budget/compensation signals, required stack, urgency, contact route, reputation risk, and match hints.
- **Targeting Focus**: Python, AI automation, data/backend, agentic tooling, smart contracts, web3 integrations, crypto infra, bots, dashboards, and rapid MVP builds.

### 2.3 Hermes Skill Lattice (Core Intelligence)
Hermes Agent runs persistently and manages:
- **Scout Skill**: Ingests opportunities/signals → scores against Profile using local model or Grok for X-native public context → produces ranked list.
- **Qualifier Skill**: Filters for Python/web3 fit, budget quality, buyer intent, scam risk, urgency, likelihood of response, and whether the opportunity is worth outreach.
- **Tailor Skill**: Takes ranked opportunity + Profile → generates tailored proposal, bid, DM, email, or resume slice. Hermes improves this skill from historical response/win rates.
- **Executor Skill**: Prepares action payload → asks Risk, Approval & Autopilot Policy Service whether approval is required or an autopilot policy applies → performs low-risk local actions directly and executes reputation-risk external actions only after approval or matching scoped autopilot policy.
- **Reflector Skill** (Hermes-native loop): Periodically or on trigger:
  - Analyzes submission outcomes (responses, interviews, rejections).
  - Identifies patterns.
  - Writes or upgrades permanent skill files (e.g., "High-Conversion DC Contract Proposal v3").
  - Updates internal user model for better future tailoring.

Skills are stored as versioned files/modules that Hermes loads and can modify.

### 2.4 Risk, Approval & Autopilot Execution Engine
- **Risk Classifier** determines whether an action is low, medium, or high reputation risk.
- **Approval Cockpit** (full-stack UI view):
  - Side-by-side: Original vs Tailored materials.
  - Exact outbound payload, destination, account/identity used, match score, risk assessment, platform policy notes.
  - Operator actions: Approve / Edit / Reject / Defer / escalate platform risk.
- Approval is mandatory by default for reputation-risk actions: submissions, outreach, account/profile modification, credential use, uploads, bids, and medium/high-risk browser automation.
- Approval is not mandatory for low-risk internal operations: public discovery, normalization, dedupe, local ranking, qualification, drafting, simulation, metrics, and local reflection.
- Scoped Autopilot can execute reputation-risk sends only when an explicit policy matches: platform, channel/account, template type, max daily sends, max bid/budget, minimum match score, scam-risk ceiling, and cooldowns.
- Full immutable audit log of every decision and material action.

### 2.5 Hybrid LLM Router
- **Local Path** (default for private data): Ollama running Hermes-compatible or strong local models (e.g., Qwen2.5, Llama 3.1 derivatives).
- **Grok/API Path**: Used for X-native public signal analysis, non-sensitive heavy reasoning, or when local model lacks capability. Operator-configurable; private profile/resume/credentials remain local unless explicitly permitted.
- Router decides per skill invocation based on data sensitivity flags.

### 2.6 Full-Stack Command Deck (Primary UX Layer)
- Tauri desktop shell.
- SvelteKit frontend with TypeScript.
- Three.js visualization layer for opportunity constellations, risk maps, and timelines.
- Local Python FastAPI service for vault, scanners, Hermes orchestration, risk gating, and audit logs.
- CLI remains a secondary utility surface for automation, debugging, recovery, and scripted operations.


## 3. Data Models (High-Level)
- `Profile`: Structured professional identity.
- `ProjectSignal`: Social/community signal that may indicate buying intent, hiring, bounties, grants, or project demand.
- `Opportunity`: Normalized job/gig/contract/bounty/marketplace lead.
- `Application`: Link between Opportunity + tailored artifacts + status + outcome.
- `OutreachDraft`: Personalized proposal, bid, DM, or email with target, channel, payload hash, and model provenance.
- `Outreach`: Send messages like emails, to reach out to client or recruiters/managers
- `Skill`: Hermes-managed persistent capability (versioned).
- `AutopilotPolicy`: Operator-defined scope for allowed automated sends/submissions.
- `ActionProposal`: Proposed local or external action with payload hash, destination, risk classification, approval/autopilot decision, and policy reference when applicable.
- `ApprovalDecision`: Operator decision for reputation-risk actions.
- `AuditEvent`: Immutable log of all significant actions.

Full Pydantic models defined in code (see tasks MON-006).

## 4. Key Flows
1. **Signal Discovery Flow**: X/Discord/marketplace/crypto board scanners → ProjectSignal/Opportunity normalization → dedupe + semantic memory → Scout/Qualifier Skills → ranked opportunities presented in deck.
2. **Application/Outreach Flow**: Select or auto-qualify opportunity → Tailor Skill → Risk Classification → Approval Cockpit or scoped Autopilot policy → Executor Skill.
3. **Evolution Flow**: After outcome data → Reflector Skill → Updated skill files + improved future performance.
4. **Full-Stack UX Flow**: Tauri/Svelte command deck → local FastAPI service → Vault/Scanner/Hermes/Risk/Autopilot services → encrypted storage + audit log.

## 5. Security & Privacy Model
See [SECURITY.md](SECURITY.md) for detailed threat model and controls. Core rules:
- Credentials encrypted at rest and only decrypted in-memory for approved actions.
- No raw personal data sent to external LLMs without explicit operator consent.
- All material actions logged; reputation-risk actions are gated by approval or scoped autopilot policy.

## 6. Integration Points
- **Hermes Agent**: Primary runtime and skill management system.
- **Ollama**: Local model serving.
- **X API + Grok API**: Public signal discovery and X-native qualification/drafting for non-sensitive context.
- **Discord API/Bot**: Approved server/channel monitoring and signal capture.
- **Marketplace/Crypto Board APIs/RSS/Email**: Upwork/Fiverr alerts, crypto job boards, bounties, grants, and saved searches.
- **Playwright**: Controlled browser automation (whitelisted and compliant workflows only).
- **Tauri + SvelteKit + Three.js**: Primary full-stack command deck.
- **FastAPI**: Local backend API for the desktop app.
- **Future**: Potential n8n/Make.com bridges for email sources if needed.

## 7. Evolution Path
Phase 0–2 focus on the full-stack foundation, encrypted vault, risk-based gates, and strong Hermes integration.  
Later phases introduce more autonomy, better visualization, and productization pathways while preserving the core principles in [PRINCIPLES.md](PRINCIPLES.md).

---

*This architecture is derived from and must remain consistent with the Source of Truth.*
