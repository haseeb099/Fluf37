# Security and compliance

Technical controls in the OSS codebase (not legal advice).

## Threat model (summary)

| Asset | Risk | Mitigation (v0.9) |
|-------|------|-------------------|
| REST API | Unauthorized pipeline | API key + JWT (`AUTH_MODE`) + RBAC |
| WebSocket | Open pipeline trigger | Optional `NEXUS_WS_REQUIRE_AUTH`; API key or JWT via query/`AUTH` |
| Webhooks | Spoofed ingest | HMAC when `NEXUS_DEMO_MODE=true` is **false** (pre-live enforces HMAC) |
| Audit log | Tampering | SHA-256 hash chain + `GET /api/v1/audit/verify` |
| Role escalation | Client-forged admin | `trust_client_role()` — **off** in pre-live and production-like modes |
| Memory | Cross-tenant bleed | Header tenancy only; shared DB paths (roadmap: isolation) |

## Authentication

- **API key** — `X-Nexus-Key` vs `NEXUS_API_KEY`.
- **JWT** — `POST /api/v1/auth/token` → `Authorization: Bearer` on protected routes.
- **Modes** — `AUTH_MODE`: `api_key_only` | `jwt_optional` | `jwt_required`.

## Authorization (RBAC)

| Role | Capabilities |
|------|----------------|
| `viewer` | Read sources status, decisions, memory, audit verify |
| `analyst` | Run pipeline (REST/WS), sync connectors, view audit tail |
| `admin` | Connect/disconnect sources, export audit |

**Role source of truth**

| Mode | How role is set |
|------|-----------------|
| JWT request | `role` claim from token (issued by `/auth/token`) |
| API key + `NEXUS_DEMO_MODE=true` + `NEXUS_TRUST_CLIENT_ROLE=true` | `X-Nexus-Role` header (local demo only) |
| API key + pre-live or `NEXUS_DEMO_MODE=false` | Forced `viewer` on API key; elevated roles only via admin JWT at token issuance |

Production: terminate TLS at gateway; map IdP groups to JWT `role`; never trust `X-Nexus-Role` from browsers.

## Pre-live mode (`NEXUS_PRE_LIVE_MODE=true`)

- Same **deterministic demo pipeline** as `NEXUS_DEMO_MODE` (synthetic data + demo LLM).
- **Production-like RBAC** — `trust_client_role()` is false; HMAC ingest enforced.
- Use for dress-rehearsal before `NEXUS_DEMO_MODE=false`.

## Audit and pipeline trace

- **LLM audit** — `LLMClient` appends token usage entries.
- **Pipeline trace** — `PipelineTracer` writes `pipeline_start`, `pipeline_state`, `agent_complete`, `pipeline_complete` to `data/audit.jsonl`.
- **Correlation** — `correlation_id` on `PIPELINE_STATE` WebSocket/REST events; stored in audit payload preview.
- **Endpoints** — `GET /api/v1/audit/verify`, `GET /api/v1/audit/recent` (analyst+), `GET /api/v1/audit/export` (admin).

## Data handling

- Demo / pre-live: synthetic data only.
- Live mode: your DPAs and retention policies apply.
- Do not embed raw PII in vector metadata.

## Reporting vulnerabilities

See [SECURITY.md](../SECURITY.md).
