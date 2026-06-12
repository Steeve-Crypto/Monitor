# Security & Operational Model

**Status**: Foundational. Must be followed for all credential and action handling.  
**Last Updated**: 2026-06-11

## 1. Core Security Posture
The operator’s credentials, professional identity, and decision authority never leave their control.

- Zero-trust on external services for sensitive data.
- Encryption at rest for all persistent secrets.
- Human approval required before reputation-risk actions by default; scoped autopilot may execute only within explicit operator-defined policy boundaries for trusted platforms/actions.
- Full auditability.

## 2. Encrypted Identity Vault
- **Storage**: Local only. Credentials and sensitive profile sections are encrypted using the `cryptography` library (AES-GCM or equivalent) with a master password or OS keyring integration.
- **Access Pattern**: Vault is unlocked in-memory only during an approved session or specific approved action. Decrypted data is never written back to disk in plaintext.
- **Key Management**: Operator-controlled master key. No cloud key escrow.
- **Schema**: Clear separation between public profile data (skills, bio) and encrypted credential store.

## 3. LLM Usage Rules
- **Local LLM Default**: All operations involving resume content, personal bio, or tailored materials use local models via Ollama first.
- **API LLM Fallback**: Only used for non-sensitive reasoning (e.g., general opportunity ranking logic without personal data). Operator must explicitly allow API usage for a session.
- **No Raw Credentials**: Under no circumstances are raw passwords, API keys, or full resume text sent to external LLM providers.

## 4. Platform Interaction Rules
- **API/Webhook/RSS-First**: Preferred method for discovery and submission. X, Discord, marketplaces, and crypto job boards should use official APIs, bot permissions, RSS/email alerts, or documented endpoints where possible.
- **Browser Automation**: Strictly limited to platforms and workflows the operator has explicitly whitelisted in the Vault. Uses Playwright for compliant operator-authorized workflows; avoids patterns that intentionally bypass platform controls.
- **Rate Limiting & Logging**: All automated interactions are rate-limited and fully logged with timestamps and outcomes.
- **Reputation-Risk Actions**: Account creation/modification, proposals, bids, submissions, DMs/emails, uploads, credential use, and medium/high-risk browser automation require explicit operator approval unless a scoped autopilot policy authorizes that exact action class. Agent proposes the action; human confirms or policy executes within limits.

## 5. Risk-Based Human-in-the-Loop Controls
- Every reputation-risk action requires explicit approval in the Command Deck by default.
- Reputation-risk actions include submissions, proposals, bids, DMs/emails, account/profile modification, credential use, uploads, and platform interactions classified medium/high risk.
- Low-risk local operations — public discovery, X/Discord monitoring where authorized, normalization, dedupe, local ranking, qualification, drafting, simulation, metrics, and reflection — can execute without approval.
- Scoped autopilot policies may authorize automated sends/submissions only with explicit limits: platform/account/channel whitelist, template family, max sends/day, cooldowns, max bid/budget, required match score, scam-risk ceiling, and kill switch.
- Operator can review full proposed reputation-risk action (what will be sent, to where, as whom, with which credentials/profile data) before approval or before enabling an autopilot policy.

## 6. Audit & Observability
- Immutable local audit log of:
  - All opportunity discoveries and rankings
  - All tailoring actions
  - All approval decisions and executions
  - Hermes skill creation / evolution events
- Logs are queryable from the Command Deck.

## 7. Threat Model & Mitigations
- **Platform Detection/Ban**: Mitigated by official API/webhook/RSS preference, whitelisting, conservative rate limits, compliance checks, and human/autopilot-policy oversight.
- **Credential Theft**: Mitigated by local encryption + in-memory-only decryption + no cloud transmission.
- **Over-Automation / Reputation Damage**: Mitigated by risk-based approval gates for reputation-impacting actions and quality-focused tailoring (not mass application).
- **Data Leakage**: Mitigated by local-first design and strict LLM routing rules.

## 8. Operational Security Recommendations
- Run on a dedicated or well-secured local machine / VM.
- Regular encrypted backups of the Vault (operator-managed).
- Review audit logs periodically.
- Start with high-signal, lower-risk platforms while the system matures.
- Never share master password or decrypted vault exports.

## 9. Future Hardening
- Optional hardware-backed key storage (e.g., YubiKey integration).
- More granular per-platform permission scopes.
- Automated anomaly detection in submission patterns (via Reflector).

---

**Rule of Thumb**: If it can affect your identity, accounts, credentials, public messaging, bids, submissions, or professional reputation, it must be encrypted where sensitive, logged, risk-classified, and either explicitly approved by you or covered by a scoped autopilot policy you enabled. Low-risk local automation can proceed without approval.

This document takes precedence on all security matters and must be updated before any change to credential or action handling.
