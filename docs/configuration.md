# Configuration

All settings load from `.env` via `backend/config.py` (`NexusConfig`, pydantic-settings).

## Core

| Variable | Default | Notes |
|----------|---------|-------|
| `NEXUS_DEMO_MODE` | `true` | **Keep true** for eval, CI, and sales demos |
| `NEXUS_PRE_LIVE_MODE` | `false` | Demo pipeline + production-like RBAC + HMAC ingest |
| `NEXUS_TRUST_CLIENT_ROLE` | `true` | Demo only: honor `X-Nexus-Role` on API-key auth |
| `NEXUS_API_KEY` | `demo-key` | Rotate in production; sent as `X-Nexus-Key` |
| `NEXUS_DEMO_SEED` | `42` | Passed to `generate_demo_data.py` |
| `CORS_ORIGINS` | localhost:3000 | Comma-separated |

## LLM

| Variable | Default | Notes |
|----------|---------|-------|
| `NEXUS_LIVE_LLM` | `false` | Use live provider while demo/pre-live synthetic data runs |
| `LLM_PROVIDER` | `anthropic` | `anthropic` \| `openai` \| `groq` |
| `ANTHROPIC_API_KEY` | `demo` | Required when `LLM_PROVIDER=anthropic` |
| `OPENAI_API_KEY` | `demo` | Required when `LLM_PROVIDER=openai` |
| `GROQ_API_KEY` | `demo` | Required when `LLM_PROVIDER=groq` — [console.groq.com](https://console.groq.com) |
| `GROQ_MODEL` | `llama-3.3-70b-versatile` | Groq model id |
| `GROQ_BASE_URL` | `https://api.groq.com/openai/v1` | OpenAI-compatible endpoint |

`LLMClient` uses live APIs when `uses_live_llm()` is true (provider key set + `NEXUS_LIVE_LLM=true` or demo off).

## Auth — **Shipped** (v0.9)

| Variable | Default | Notes |
|----------|---------|-------|
| `AUTH_MODE` | jwt_optional | `api_key_only` \| `jwt_optional` \| `jwt_required` |
| `JWT_SECRET` | change-me | Signs tokens from `POST /api/v1/auth/token` |
| `NEXUS_WS_REQUIRE_AUTH` | false | Require token on WebSocket `RUN_PIPELINE` |

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

## Install profiles

| File | When |
|------|------|
| `requirements.txt` | Demo/CI core (Python 3.11–3.13); in-memory vector fallback |
| `requirements-vector.txt` | ChromaDB persistence (Python 3.11–3.12 recommended on Windows) |

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
