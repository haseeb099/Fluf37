# API overview

Base URL: `http://localhost:8000` (configurable). Interactive docs: `/docs`.

## Authentication

Protected REST routes require:

```http
X-Nexus-Key: <NEXUS_API_KEY>
```

Optional headers:

| Header | Default | Purpose |
|--------|---------|---------|
| `X-Nexus-Tenant-Id` | `default` | Isolate orchestrator/connector manager |
| `X-Nexus-Role` | `admin` in dev | `viewer` \| `analyst` \| `admin` for RBAC |

**Production note:** Set roles at the API gateway; do not trust client-supplied `X-Nexus-Role`.

## Health

| Endpoint | Response |
|----------|----------|
| `GET /health` | `status`, `demo_mode`, `agents` (per-agent state when initialized) |
| `GET /ready` | `ready`, `connectors_registered`, `memory` stats |

## Nexus pipeline

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/nexus/run/demo` | Run full pipeline synchronously (returns event count) |
| GET | `/api/v1/nexus/status` | `pipeline_state`, `context_keys` |

## WebSocket

**URL:** `ws://localhost:8000/ws/nexus/stream` (see `NEXT_PUBLIC_WS_URL`)

### Client → server

```json
{"type": "PING"}
{"type": "RUN_PIPELINE", "mode": "demo"}
{"type": "RESET"}
```

### Server → client

Structured `AgentEvent` JSON (`type`, `agent_id`, `data`) plus final:

```json
{"type": "PIPELINE_STATE", "agent_id": "orchestrator", "data": {"state": "COMPLETE", "report": {}}}
```

## Integrations

| Method | Path | Role |
|--------|------|------|
| GET | `/api/v1/sources/status` | All source connection statuses |
| POST | `/api/v1/connect/{source}` | Connect (admin) |
| DELETE | `/api/v1/connect/{source}` | Disconnect (admin) |
| POST | `/api/v1/connect/{source}/sync` | Manual sync |
| GET | `/api/v1/connectors` | List registered connector types |

`source` ∈ `crm` | `erp` | `bank` | `trading` | `news` | `custom` | `webhook`

## Ingest

```http
POST /ingest/{source}
X-Nexus-Tenant-Id: default
X-Nexus-Signature: <hmac-sha256-hex of body>
```

When `NEXUS_DEMO_MODE=true`, signature check is skipped.

## Decisions

| Method | Path |
|--------|------|
| GET | `/api/v1/decisions/` |
| GET | `/api/v1/decisions/{decision_id}` |
| POST | `/api/v1/decisions/{decision_id}/outcome` |

Body for outcome:

```json
{"outcome": "correct"}
```

## Memory

| Method | Path |
|--------|------|
| GET | `/api/v1/memory/search?q=...` |
| GET | `/api/v1/memory/graph` |
| GET | `/api/v1/memory/stats` |

## Evolution

| Method | Path |
|--------|------|
| GET | `/api/v1/evolution/report` |
| POST | `/api/v1/evolution/approve/{cycle_id}` |

## Audit

| Method | Path |
|--------|------|
| GET | `/api/v1/audit/verify` |
| GET | `/api/v1/audit/export` |

## Example: demo run

```bash
curl -s http://localhost:8000/health
curl -s http://localhost:8000/api/v1/sources/status -H "X-Nexus-Key: demo-key"
curl -s -X POST http://localhost:8000/api/v1/nexus/run/demo -H "X-Nexus-Key: demo-key"
```

## Frontend client

See `frontend/src/lib/api.ts` — hardcoded `demo-key` for local dev; use env-based key in production builds (roadmap).
