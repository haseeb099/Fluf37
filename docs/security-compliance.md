# Security and compliance

This document describes **technical controls in the OSS codebase**. It is not legal or compliance advice. Engage your counsel for GLBA, SOC 2, MiFID, or sector-specific obligations.

## Threat model (summary)

| Asset | Risk | Mitigation today | Roadmap |
|-------|------|------------------|---------|
| API | Unauthorized pipeline runs | `X-Nexus-Key` | JWT + rate limits |
| WebSocket | Open pipeline trigger | None | Token auth |
| Webhooks | Spoofed ingest | HMAC (non-demo) | Key rotation, replay window |
| Audit log | Tampering | Hash chain + `/audit/verify` | Remote append-only store |
| Memory stores | Data at rest exposure | Local paths | Encryption at rest, tenant isolation |
| LLM prompts | PII leakage | Demo canned text | Redaction layer |

## Authentication and authorization

- **API key** — Compare `X-Nexus-Key` to `NEXUS_API_KEY` (`backend/auth/deps.py`).
- **RBAC** — `require_role("admin")` on connect/disconnect and audit export; role from header (trust boundary issue for production).
- **JWT** — `JWT_SECRET` in config; **not applied** to FastAPI routes yet.

## Audit and explainability

- `AuditLog` (`backend/utils/audit_log.py`) — append-only JSONL with `hash` / `prev_hash` chain.
- Endpoints: `GET /api/v1/audit/verify`, `GET /api/v1/audit/export` (admin).
- Agent outputs include `chain_of_thought` and `counterfactual` fields where applicable (blind spots).

## Data handling

- **Demo mode** — Synthetic data only; safe for public demos and CI.
- **Live mode** — You are responsible for vendor DPAs, retention, and regional residency.
- **Embeddings** — Do not embed raw account numbers or national IDs; normalize and minimize fields in `SourceData`.
- **Credentials** — `CredentialStore` is in-memory; use a vault (HashiCorp, cloud KMS) in production.

## Multi-tenancy

- Header `X-Nexus-Tenant-Id` selects orchestrator and connection manager instances.
- **No database-level tenant isolation** — all tenants share SQLite/Chroma paths unless you deploy per-tenant stacks or extend storage (roadmap).

## Privacy

- Minimize fields in connectors and logs.
- Provide data export/delete processes in your product layer (not automated in OSS core).
- Document subprocessors if you enable live LLM providers.

## Compliance-oriented practices (recommended)

1. **Human approval** before evolution weight changes (`POST /api/v1/evolution/approve/{cycle_id}`).
2. **Decision outcomes** logged for retrospective review (`POST .../outcome`).
3. **Simulation before action** — run full pipeline including adversarial step before executing trades or credit decisions in production workflows.
4. **Retention policy** — rotate `data/audit.jsonl` and SQLite per your records schedule.
5. **Access reviews** — map `X-Nexus-Role` to IdP groups when JWT lands.

## Reporting vulnerabilities

Report security issues privately to the maintainers (add `SECURITY.md` with contact email when publishing). Do not open public issues for exploitable flaws.
