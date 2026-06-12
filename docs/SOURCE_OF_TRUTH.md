# Monitor — Source of Truth

**Status**: Authoritative. All other documents and code must reference or derive from this file.  
**Last Updated**: 2026-06-12  
**Version**: 0.1.0 

## 1. Purpose & Scope
Monitor is a **local-first, Hermes-native autonomous system** that:
- Discovers project signals, freelance gigs, bounties, contracts, and roles across X, Discord, Upwork, Fiverr, crypto job boards, RSS/API sources, email alerts, and whitelisted communities.
- Maintains a sovereign encrypted profile vault containing resume, portfolio, credentials, and structured professional data.
- Uses the Hermes self-improving agent loop to create, refine, and persist skills for opportunity matching, tailoring, and application execution.
- Executes reputation-risk actions behind explicit approval gates by default, with optional scoped autopilot policies for pre-authorized platforms, proposal templates, rate limits, and budget/category constraints.
- Evolves its effectiveness over time through outcome reflection and skill evolution.
- Delivers a dark premium futuristic full-stack command deck experience.

**In Scope (MVP)**:
- Encrypted local Identity Vault
- Multi-source opportunity discovery from X, Discord, Upwork, Fiverr, crypto job boards, RSS/API feeds, email alerts, and selective whitelisted browser workflows
- Hermes-powered Scout, Tailor, and Executor skills
- Risk-based approval/autopilot workflow for reputation-risk actions
- Basic reflection loop for skill improvement
- Full-stack desktop command deck (Tauri + Svelte/Vite + Three.js)
- Local Python API service for vault, scans, Hermes orchestration, risk gating, and audit logs
- CLI utilities for automation, debugging, and recovery

**Out of Scope (MVP)**:
- Unbounded autonomous reputation-risk actions without operator-defined autopilot policies
- Cloud-hosted version
- Mobile app
- Integration with unapproved/high-risk platforms or automation patterns that violate platform rules

**Primary Success Metric**: Consistent flow of qualified Python, AI automation, and web3 gig leads that convert into paid projects, interviews, retainers, or contract wins.

## 2. Core Architecture Summary
See [ARCHITECTURE.md](ARCHITECTURE.md) for full details. High-level components:

- **Encrypted Identity Vault** — Sovereign storage for all personal/professional data. Never transmitted.
- **Signal & Opportunity Mesh Scanner** — X/Grok, Discord, marketplace, crypto job board, RSS/API, email, and whitelisted browser adapters.
- **Persistent Signal Mesh Store** — Local JSON-backed persistence for normalized signals and opportunities, configurable with `MONITOR_SIGNAL_MESH_STORE_PATH`; default path is `.monitor/signal_mesh_store.json`.
- **Hermes Skill Lattice** — Self-evolving skills (Scout, Tailor, Executor, Reflector). Hermes writes and improves permanent skill files.
- **Risk, Approval & Autopilot Execution Engine** — Human review cockpit by default when a proposed action creates reputation, account, credential, or external-identity risk; scoped autopilot may execute only pre-authorized action classes within explicit limits.
- **Hybrid LLM Router** — Local-first for private data; API models for heavy reasoning.
- **Command Deck (UX)** — Full-stack dark premium futuristic interface (holographic opportunity constellation, encrypted vault visuals, quantum application timelines), with CLI as a secondary utility surface.

**Data Flow (Simplified)**:
Profile Vault → Signal/Opportunity Scanner → Dedupe + Semantic Memory → Hermes Scout/Qualifier Skill → Ranked Python/web3 opportunities → Hermes Tailor Skill → Personalized proposal/DM/email artifacts → Risk Classification → Approval Cockpit or scoped Autopilot policy → Hermes Executor Skill → Submission/Outreach/Local Update + Logging → Hermes Reflector Skill (periodic evolution).

**Current Implementation Baseline**: FastAPI exposes `/api/health`, encrypted profile vault APIs, `/api/signals`, `/api/opportunities`, `/api/scans/{source}/run`, `/api/signals/{signal_id}/qualify`, and `/api/store/stats`. X, Discord, marketplace, and generic crypto sources are disabled until real live adapters/credentials are configured; unconfigured scans return 503 and never generate fake/demo leads. The `crypto_rss` source can ingest an operator-configured public `http`/`https` RSS feed via `MONITOR_CRYPTO_RSS_FEED_URL`. The local store persists normalized signals/opportunities, dedupes signals by source platform + source id, and persists deterministic qualification scores. Semantic/vector memory and live platform credential integrations remain pending.

## 3. Key Decisions & Constraints
- **Hermes Integration**: Primary runtime. We extend Hermes with custom persistent skills rather than building a parallel agent framework from scratch.
- **Local Sovereignty**: All credentials, resume tailoring involving personal data, and decision-making on sensitive actions stay on-device. Ollama + Hermes local models preferred for private operations.
- **Risk-Based Autonomy**: Human approval is the default for reputation-risk actions. Low-risk internal operations such as discovery, normalization, ranking, qualification, drafting, simulation, metrics, and local reflection may run without approval. The operator may enable scoped autopilot for trusted platforms/actions with explicit constraints: platform whitelist, proposal template family, max sends per day, max bid/budget, gig category, credential scope, and kill switch.
- **Platform Policy Compliance**: API/webhook/RSS-first. Browser automation only on explicitly whitelisted compliant workflows with conservative rate limiting. No violation of platform ToS by design.
- **Self-Improvement Model**: Hermes native loop — successful/failed applications feed the Reflector, which creates or upgrades skill files (e.g., "DC Contract Proposal Specialist v2").
- **UX Philosophy**: The primary product is a full-stack dark premium command deck, not a terminal-first CLI. Every interface element must feel premium, space-dark, and futuristic. No corporate SaaS aesthetic. Neural, holographic, cyberpunk-command-deck vibe.
- **Revenue Focus**: The system exists primarily to generate income for the builder through Python, AI automation, and web3 gigs/contracts. Secondary path: mature into a premium product for other agentic engineers.

## 4. References
- [PRINCIPLES.md](PRINCIPLES.md) — Non-negotiable design philosophy.
- [ARCHITECTURE.md](ARCHITECTURE.md) — Detailed component design, data models, and flows.
- [TASKS.md](TASKS.md) — Phased task breakdown with IDs (MON-XXX). All implementation work traces back to tasks listed here.
- [SECURITY.md](SECURITY.md) — Credential encryption model, threat model, and operational security rules.
- [FULL_STACK_APP_PLAN.md](FULL_STACK_APP_PLAN.md) — Product/UX stance, app architecture, data contracts, implementation phases.
- Hermes Agent documentation (Nous Research) — https://hermes-agent.nousresearch.com/docs/

## 5. Change Management
Any modification to scope, architecture, safety model, or Hermes integration **must** be reflected in this Source of Truth first, then propagated to dependent documents and code.

**Current Phase**: Phase 2 — Signal Discovery & Persistent Signal Mesh  
**Next Milestone**: Complete opportunity dedupe + semantic/vector memory, add richer crypto source presets, then implement Tailor + Approval Cockpit before enabling any executor/autopilot sends. Live Discord and X/Grok integrations remain behind platform-safe credential gates.

---

*This document is the single source of truth. When in doubt, return here.*
