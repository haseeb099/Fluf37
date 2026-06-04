# Configuration

All settings load from `.env` via `backend/config.py` (`NexusConfig`, pydantic-settings).

## Core

| Variable | Default | Notes |
|----------|---------|-------|
| `NEXUS_DEMO_MODE` | `true` | **Keep true** for eval, CI, and sales demos |
| `NEXUS_API_KEY` | `demo-key` | Rotate in production; sent as `X-Nexus-Key` |
| `NEXUS_DEMO_SEED` | `42` | Passed to `generate_demo_data.py` |
| `CORS_ORIGINS` | localhost:3000 | Comma-separated |

## LLM (roadmap for live)

| Variable | Default | Notes |
|----------|---------|-------|
| `ANTHROPIC_API_KEY` | `demo` | Unused when demo mode on |
| `OPENAI_API_KEY` | `demo` | Unused when demo mode on |

`LLMClient` does not call live APIs yet when `NEXUS_DEMO_MODE=false`.

## Auth (partial)

| Variable | Default | Notes |
|----------|---------|-------|
| `JWT_SECRET` | change-me | **Not wired** to routes; roadmap |

## Connectors

| Variable | Default | Notes |
|----------|---------|-------|
| `NEXUS_ENABLED_CONNECTORS` | crm,erp,bank,trading,news | Registered types |
| `NEXUS_ENABLE_CRM` | false | Live fetch (returns empty today) |
| `NEXUS_ENABLE_ERP` | false | |
| `NEXUS_ENABLE_BANK` | false | Uses Plaid stub when true |
| `NEXUS_ENABLE_TRADING` | false | Uses Alpaca stub when true |
| `NEXUS_ENABLE_NEWS` | false | |

## Webhook ingest

| Variable | Purpose |
|----------|---------|
| `INGEST_HMAC_SECRET_CRM` | HMAC for `POST /ingest/crm` |
| `INGEST_HMAC_SECRET_BANK` | HMAC for bank ingest |
| `INGEST_HMAC_SECRET_ERP` | HMAC for ERP ingest |

## Vendor credentials (roadmap / stubs)

Plaid: `PLAID_CLIENT_ID`, `PLAID_SECRET`, `PLAID_ENV`

Alpaca: `ALPACA_API_KEY`, `ALPACA_SECRET_KEY`, `ALPACA_BASE_URL`

CRM/ERP: see `.env.example` for Salesforce, HubSpot, NetSuite, QuickBooks placeholders.

## Memory paths

| Variable | Default |
|----------|---------|
| `VECTOR_DB_PATH` | `./data/chroma` |
| `GRAPH_DB_PATH` | `./data/graph.json` |
| `SQLITE_PATH` | `./data/nexus.db` |

Mount these as persistent volumes in Docker/Kubernetes.

## Frontend

| Variable | Default |
|----------|---------|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` |
| `NEXT_PUBLIC_WS_URL` | `ws://localhost:8000/ws/nexus/stream` |

## Agent tuning

Defined in `NexusConfig` (no env alias unless added):

- `adversarial_max_iterations` (default 5)
- `traceback_max_results` (default 5)
- `evolution_cycle_days`, `min_feedback_for_update`, `max_weight_change_per_cycle`

## Plugin loading

`CONNECTOR_PLUGINS` is documented in [CONNECTORS.md](CONNECTORS.md) but **not implemented** in `config.py` yet.
