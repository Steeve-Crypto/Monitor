# Tasks & Roadmap

**Status**: Living document. Mirror or import into Linear/Kanban tool as needed.  
**Last Updated**: 2026-06-11  
**Current Phase**: Phase 2 — Signal Discovery & Persistent Signal Mesh

All tasks use the prefix **MON-** (Monitor).  
Format: `[MON-XXX] Task title` — Status — Priority — Dependencies — Notes

Use this document as the working task list. Update status as work progresses. Reference specific task IDs in commits and discussions.

---

## Phase 0: Foundation & Encrypted Vault (Current)

- [MON-001] Initialize project directory structure and virtual environment — **Done** — P0
- [MON-002] Create core documentation set (README, Source of Truth, Principles, Architecture, Tasks, Security) — **Done** — P0 — Updated for Monitor naming, full-stack app, X/Discord/marketplace/web3 signal focus, scoped autopilot, and persistence baseline
- [MON-003] Design and implement Encrypted Identity Vault module (local encryption, keyring integration, profile JSON schema) — **To Do** — P0 — Depends on MON-002
- [MON-004] Build Profile Manager API + secondary CLI utilities (view, update, export, backup) — **To Do** — P0 — Depends on MON-003
- [MON-005] Integrate Hermes Agent runtime skeleton + verify local model loading — **To Do** — P0
- [MON-006] Define initial data models (Profile, ProjectSignal, Opportunity, OutreachDraft, Application, Skill, AutopilotPolicy, ActionProposal, ApprovalDecision, AuditEvent) using Pydantic — **Done** — P0 — Implemented in `apps/api/src/monitor_api/models.py` with tests

## Phase 1: Full-Stack Foundation & Command Deck

- [MON-007] Create monorepo structure (`apps/desktop`, `apps/api`, `packages/shared`) — **Done** — P0 — Depends on MON-002
- [MON-008] Implement local FastAPI service with health endpoint and typed API contract baseline — **Done** — P0 — Depends on MON-006 — Includes `/api/health`, signals, opportunities, scan run, and store stats endpoints
- [MON-009] Implement Tauri + SvelteKit shell with dark premium command deck frame — **Done** — P0 — Depends on MON-007 — Implemented as Tauri-ready Svelte/Vite shell after SvelteKit SSR build proved unreliable on the mounted Windows path
- [MON-014] Wire desktop app to local API health/status and vault lock state — **Partially Done** — P0 — Depends on MON-008, MON-009 — API health contract wired; vault lock state pending MON-003

## Phase 2: Signal Discovery & Hermes Scout/Qualifier

- [MON-010] Implement Signal Mesh Scanner adapter interface (API/webhook/RSS/email/browser workflow abstraction) — **Done** — P1 — Depends on MON-006 — Mock-backed X, Discord, marketplace, and crypto adapters implemented in `apps/api/src/monitor_api/scanners.py`
- [MON-011] Create Hermes Scout Skill (ranks opportunities/signals against profile using local model and optional Grok for public X context) — **To Do** — P1 — Depends on MON-005, MON-010
- [MON-012] Build opportunity qualification logic for Python/web3 fit, buyer intent, budget quality, urgency, scam risk, and response likelihood — **To Do** — P1
- [MON-013] Add X/Grok signal adapter for public posts, buying-intent searches, founder/project hiring signals, and DM-worthy threads — **Partially Done** — P1 — Depends on MON-010 — Mock adapter and API contract done; live X/Grok credentials/API integration pending
- [MON-015] Add Discord approved-server/channel adapter for gig posts, bounties, grant leads, and hiring requests — **Partially Done** — P1 — Depends on MON-010 — Mock adapter and API contract done; live Discord bot integration pending
- [MON-016] Add Upwork/Fiverr marketplace adapters via official interfaces, alerts, or whitelisted compliant browser workflows — **Partially Done** — P1 — Depends on MON-010 — Mock marketplace adapter and API contract done; live ingestion pending
- [MON-017] Add crypto job board/bounty adapters (Web3.career, CryptoJobsList, Cryptocurrency Jobs, Remote3, Dework/Gitcoin-style sources) — **Partially Done** — P1 — Depends on MON-010 — Mock crypto adapter and live-safe `crypto_rss` RSS/HTTP ingestion done; board-specific presets still pending
- [MON-018] Implement dedupe + semantic opportunity memory with vector search — **In Progress** — P1 — Depends on MON-006, MON-010 — JSON-backed persistent signal/opportunity store and `(source_platform, source_id)` signal dedupe done; semantic/vector search pending

## Phase 2A: Persistent Signal Mesh Storage

- [MON-019] Implement local JSON-backed Signal Mesh persistence for signals and opportunities — **Done** — P1 — Stores `ProjectSignal` and `Opportunity` collections in `.monitor/signal_mesh_store.json` by default, configurable via `MONITOR_SIGNAL_MESH_STORE_PATH`, with atomic writes and `/api/store/stats`

## Phase 3: Tailoring, Risk-Based Approval Cockpit, Scoped Autopilot & Execution

- [MON-020] Develop Hermes Tailor Skill for customized Upwork proposals, Fiverr replies, X DMs/replies, Discord DMs/messages, crypto board applications, and email outreach — **To Do** — P2 — Depends on MON-011, MON-012
- [MON-021] Design and implement full-stack Approval Cockpit (payload preview, destination, identity, risk scoring, approve/edit/reject/defer, policy decision) — **To Do** — P2 — Depends on MON-020
- [MON-022] Create Hermes Executor Skill with Risk, Approval & Autopilot Policy Service gate — **To Do** — P2 — Depends on MON-021
- [MON-023] Implement immutable audit logging, action proposals, approval decisions, autopilot policy decisions, payload hashes, model provenance, and submission/outreach history — **To Do** — P2
- [MON-024] Implement scoped AutopilotPolicy model and controls (platform whitelist, template family, max sends/day, cooldowns, max bid/budget, match threshold, scam-risk ceiling, kill switch) — **To Do** — P2 — Depends on MON-006, MON-021
- [MON-025] Implement local LLM/Grok routing for qualification and proposal drafting with privacy guards — **To Do** — P2 — Depends on MON-005, MON-020

## Phase 4: Self-Improvement Loop & Metrics

- [MON-030] Build Hermes Reflector Skill (analyzes responses, wins/losses, source quality, proposal performance, creates/upgrades persistent sourcing/tailoring skills) — **To Do** — P3 — Depends on MON-022
- [MON-031] Add periodic reflection trigger + skill version management — **To Do** — P3
- [MON-032] Implement success metrics dashboard (signals captured, qualified gigs, proposals/DMs sent, response rate, interview rate, win rate, revenue, source ROI) — **To Do** — P3
- [MON-033] Create feedback loop for operator to rate outcomes and feed Reflector — **To Do** — P3

## Phase 5: Polish, Futuristic UX & Hardening

- [MON-040] Full dark premium futuristic desktop polish (holographic cards, neural loading states, command deck aesthetics) — **To Do** — P4
- [MON-041] Add visual Opportunity Constellation view using Three.js — **To Do** — P4
- [MON-042] Security hardening + operational security checklist — **To Do** — P4 — Depends on SECURITY.md
- [MON-043] Documentation completion and operator runbook — **To Do** — P4

## Future / Post-MVP

- [MON-100] Optional hosted/self-hosted web dashboard mode after desktop app proves valuable
- [MON-101] Configurable risk thresholds and approval policies by platform/action type
- [MON-102] Productization path (self-hosted distribution + premium hosted offering)
- [MON-103] Advanced multi-agent orchestration on top of Hermes (if needed)

---

## How to Work This Document
1. Pick a task (start with Phase 0 items).
2. Update status to **In Progress**.
3. When complete, mark **Done** and add brief outcome note.
4. Any new requirement or architectural change must first be recorded in [SOURCE_OF_TRUTH.md](SOURCE_OF_TRUTH.md) before creating new tasks.

**Next Immediate Focus**: Add board-specific crypto RSS/source presets and first-pass qualification scoring, then Discord bot/API, then X/Grok. Add semantic scoring before enabling any scoped autopilot sends.

---

*This is the working task surface. Keep it updated so the Source of Truth and code stay in sync.*
