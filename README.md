# Monitor

**Sovereign Self-Evolving Opportunity Acquisition System**

Monitor is a local-first, Hermes-powered autonomous agent that detects project signals and paid gigs across X, Discord, Upwork, Fiverr, crypto job boards, RSS/API sources, and whitelisted communities; filters for Python, automation, AI, and web3 work; drafts personalized proposals/DMs/emails; and can execute approved or pre-authorized applications under a risk-based control model. It uses the Hermes self-improving agent architecture to evolve its own sourcing, qualification, and outreach skills over time.

Built by an agentic engineer, for agentic engineers. Dark premium futuristic interface. Local sovereignty. Revenue through landed work and future productization.

## Vision
A neural extension of your agency that operates 24/7 across the gig, crypto, and builder opportunity mesh — detecting buying intent, matching Python/web3 work, tailoring proposals, and executing high-quality outreach while you focus on high-leverage delivery.

## Core Principles
- **Sovereignty First**: Everything runs locally. Credentials and sensitive data never leave your machine.
- **Hermes-Native Self-Improvement**: The system writes and refines permanent skills from real outcomes.
- **Risk-Based Autonomy**: Discovery, ranking, qualification, drafting, and simulation run autonomously. Reputation-risk sends/submissions require approval unless the operator explicitly enables a scoped autopilot policy for trusted platforms/templates/budgets.
- **Dark Premium Futuristic UX**: Full-stack command deck with holographic opportunity views, encrypted vault aesthetics, and CLI utilities for automation/debugging.
- **Revenue Aligned**: Primary goal is landing Python, AI automation, and web3 gigs/contracts from marketplaces, crypto ecosystems, and high-signal social/community channels. Secondary: productize as premium tooling.

## Current Status
- Phase 2 baseline in progress: FastAPI backend, Pydantic contracts, encrypted local profile vault, deterministic opportunity qualification, live-safe crypto RSS ingestion, JSON-backed persistent signal/opportunity store, and Tauri-ready Svelte command deck with scan/stats/signal/opportunity UI are operational. X, Discord, marketplace, and board-specific crypto sources are disabled until real live adapters/credentials are configured; no fake/demo signal generation is used. Semantic/vector memory, Tailor, Approval Cockpit, and executor/autopilot sends are still pending.

## Implemented API Baseline
- `GET /api/health`
- `GET /api/profiles` / `POST /api/profiles` / `GET /api/profiles/{profile_id}` with `X-Vault-Password`
- `GET /api/signals` / `POST /api/signals`
- `POST /api/signals/{signal_id}/qualify`
- `GET /api/opportunities` / `POST /api/opportunities`
- `POST /api/scans/{source}/run` rejects unconfigured sources with 503 instead of generating fake data
- `POST /api/scans/crypto_rss/run` for live-safe public RSS/HTTP crypto job-board ingestion
- `GET /api/store/stats`
- Default local store: `.monitor/signal_mesh_store.json` (`MONITOR_SIGNAL_MESH_STORE_PATH` can override)
- Optional live crypto RSS feed: set `MONITOR_CRYPTO_RSS_FEED_URL` to a public `http` or `https` RSS URL before starting `apps/api`
- Default encrypted profile vault: `.monitor/profile_vault.json` (`MONITOR_PROFILE_VAULT_PATH` can override)
- Qualification is currently deterministic/local and safe for low-risk internal scoring; external sends/submissions remain disabled until Tailor + Approval Cockpit + audit gates are implemented.

## Quick Start (Planned)
```bash
git clone <repo>
cd monitor
python -m venv .venv
source .venv/bin/activate  # or Windows equivalent
pip install -r requirements.txt
# Launch command deck
python -m monitor.api  # planned local backend; desktop app launches via Tauri
```

## Documentation
- [Source of Truth](docs/SOURCE_OF_TRUTH.md) — Authoritative reference for scope, architecture, and decisions.
- [Principles](docs/PRINCIPLES.md) — Non-negotiable design philosophy.
- [Architecture](docs/ARCHITECTURE.md) — Detailed system design, data flows, and Hermes integration.
- [Tasks](docs/TASKS.md) — Phased Kanban-style task breakdown with IDs.
- [Security](docs/SECURITY.md) — Credential handling, encryption, and risk model.
- [Full-Stack App Plan](docs/FULL_STACK_APP_PLAN.md) — Product, UX, architecture, API contracts, and phased implementation plan.

## Tech Stack (Target)
- Hermes Agent (Nous Research) — core self-improving runtime
- Tauri desktop shell + Svelte/Vite frontend for the primary command deck
- Three.js for opportunity constellation and premium visualizations
- Python 3.12+ + FastAPI + Pydantic v2 local backend
- PostgreSQL/SQLite + vector index for opportunity memory, dedupe, and semantic matching
- Local LLM via Ollama for private data; Grok API optional for X-native/non-sensitive qualification and drafting
- Official APIs/webhooks first: X API/Grok, Discord bot/API, Upwork/Fiverr available interfaces, RSS, crypto job board APIs
- Playwright only for whitelisted, compliant browser workflows
- cryptography + keyring for secure vault
- CLI utilities for automation, debugging, and recovery

## Contributing / Usage
This is a personal production system first. Once proven, core skills and patterns may be open-sourced under a strong license.

**Status**: Active build. Source of Truth is the single point of reference for all future work.

---

*Built in the DC grid. Powered by Hermes. Designed for sovereignty and compounding results.*
