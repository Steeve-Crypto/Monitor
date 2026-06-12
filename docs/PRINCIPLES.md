# Monitor — Design Principles

**Status**: Non-negotiable. All architecture, code, and UX decisions must align with these principles.  
**Last Updated**: 2026-06-11

## 1. Sovereignty & Local-First
- The operator owns and controls every piece of data and every action.
- Credentials, resume content, portfolio materials, and decision logic never leave the local machine in plaintext.
- Preference for local LLMs (Ollama + Hermes-compatible models) for any operation involving personal or sensitive data.
- Cloud APIs are used only for non-sensitive reasoning or when local models are insufficient, with explicit user awareness.

## 2. Hermes-Native Self-Improvement
- The system is built around the Hermes Agent architecture (Nous Research).
- Skills are not static prompts — they are persistent, versioned artifacts that Hermes creates, refines, and reuses based on real outcomes.
- The Reflector skill runs periodically to analyze what worked, what failed, and to evolve the skill lattice autonomously.
- Over time, Monitor becomes a compounding personal advantage rather than a static tool.

## 3. Risk-Based Human Oversight (Safety)
- In Phase 0–2, **reputation-risk actions** require explicit human approval by default in the Command Deck; the operator may later enable tightly scoped autopilot for trusted platforms/actions.
- Reputation-risk actions include submissions, proposals, bids, DMs/emails, account/profile modification, credential use, uploads, and medium/high-risk browser automation.
- Low-risk internal operations — X/Discord/public source monitoring where authorized, discovery, normalization, local ranking, qualification, drafting, simulation, dashboard updates, metrics, and local reflection — can run without approval.
- The system classifies risk, proposes the action, and presents exact payloads when approval is required; the human decides on reputation-impacting execution.
- This protects reputation, prevents platform bans, and maintains ethical operation without slowing safe local automation or pre-authorized high-confidence outreach.

## 4. Dark Premium Futuristic Experience
- The primary interface is a full-stack desktop command deck, not a terminal-first CLI. Every interface the operator touches must feel like a high-end neural command system.
- Visual language: deep black backgrounds, Purple and grey accents, glassmorphism, holographic elements, subtle particle/neural effects.
- Information density is high but clarity is higher. No corporate minimalism or bright SaaS aesthetics.
- The desktop app, dashboard views, and secondary CLI utilities should evoke "commanding a sovereign agent fleet from a dark premium cockpit."

## 5. Revenue & Outcome Focus
- The primary purpose is generating real revenue through landed Python, AI automation, and web3 gigs/contracts/roles.
- Every feature must ultimately contribute to higher-quality opportunities and better conversion rates.
- Secondary objective: mature the system into a premium, defensible product that other agentic engineers will pay for (self-hosted or hosted instances).
- We optimize for signal quality over application quantity.

## 6. Platform Respect & Ethical Automation
- API/webhook/RSS-first discovery and submission where possible, including official X, Discord, marketplace, and crypto job board interfaces.
- Browser automation is used only on explicitly whitelisted compliant workflows, with conservative rate limits and full audit logging.
- We do not build or encourage systems that intentionally violate platform Terms of Service.
- The operator is always in control and fully informed of actions taken on their behalf.

## 7. Clarity & Maintainability
- Documentation is self-contained, well-structured, and cross-referenced.
- The Source of Truth is the single point of reference. Code and tasks must trace back to it.
- Complexity is accepted only when it delivers clear compounding advantage (e.g., Hermes skill evolution).

---

These principles are the foundation. Any proposed change that conflicts with them must be explicitly justified and recorded in the Source of Truth before implementation.
