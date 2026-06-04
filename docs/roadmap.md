# Roadmap

Labels match [README.md](../README.md) **What ships today**.

## MVP (current — open core v0.9)

**Goal:** Credible demo for investors, design partners, and OSS contributors.

- [x] Six-agent orchestrated pipeline with WebSocket streaming
- [x] Demo synthetic data generator (seeded)
- [x] Next.js dashboard (connections, agents, decisions, traceback, evolution)
- [x] Chroma + NetworkX + SQLite memory
- [x] Hash-chained audit log + verify API
- [x] API key + tenant header + header RBAC
- [x] HMAC webhook ingest (strict when not demo)
- [x] CI: pytest + ruff + frontend typecheck, lint, build
- [x] WebSocket authentication (optional JWT / `NEXUS_WS_REQUIRE_AUTH`)
- [x] Documented SECURITY.md contact

## v1 (near-term)

**Goal:** Pilot with sandbox/live data for one vertical (e.g. CFO + Plaid + CRM).

| Item | Outcome |
|------|---------|
| Live `LLMClient` | Anthropic/OpenAI with timeout, retries, token audit (validate in staging) |
| Plaid + Alpaca connectors | Real fetch behind `NEXUS_ENABLE_*` (stubs exist; production hardening) |
| JWT required in prod | Enforce `AUTH_MODE=jwt_required` + gateway RBAC (token route shipped in v0.9) |
| Rate limiting tuning | Per-tenant limits beyond global `slowapi` |
| Health metrics | Prometheus/OpenTelemetry in `observability/` |
| Frontend API key | `NEXT_PUBLIC_NEXUS_API_KEY` (dev); gateway in prod |
| CRM/ERP live | Salesforce or HubSpot read-only sync |
| Approval UI | Evolution cycle review in dashboard |
| Docker hardening | Non-root user, multi-stage images |

## Scale (future)

**Goal:** Multi-tenant SaaS with enterprise procurement fit.

- Tenant-isolated databases (Postgres + per-tenant Chroma or pgvector)
- Connector plugin loader (`CONNECTOR_PLUGINS`)
- Configurable approval workflows (trade, credit, vendor payment)
- Row-level security and SOC2-friendly audit export (S3 + immutability)
- Worker queue (Redis/RQ) for long pipelines
- IBKR, NetSuite, NewsAPI production connectors
- Causal inference / mutual-information scoring (PRD advanced)
- SSO (OIDC) and SCIM

## Competitive gaps we intentionally target

| Market gap | Nexus direction |
|------------|-----------------|
| Black-box copilots | Schema-validated events + audit chain |
| Alert fatigue | Blind-spot *discovery*, not more charts |
| No pre-mortem | Adversarial agent in the default pipeline |
| Session amnesia | Traceback + persistent memory |
| Integration spaghetti | `BaseConnector` + registry + webhooks |

## How to influence priority

Open an issue with: user persona, data source, and whether you need **demo**, **pilot**, or **production**. PRs that keep `pytest` green and demo checklist passing merge faster.
