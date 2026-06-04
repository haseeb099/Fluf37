# Nexus AI — Connector & Plugin API

> **Implementation status (June 2026):** Demo JSON + normalization **shipped**. Live vendor calls are **stubs or empty** unless `NEXUS_DEMO_MODE=true` and demo files are used. Plaid/Alpaca have stub clients in `backend/connectors/live/`. `CONNECTOR_PLUGINS` env loading is **roadmap** — not in `config.py` yet.

## Supported source types

| `source_type` | Built-in adapter | Demo data | Live (feature flag) |
|---------------|------------------|-----------|---------------------|
| `crm` | `crm_connector.py` | `data/demo/crm_data.json` | Salesforce, HubSpot |
| `erp` | `erp_connector.py` | `data/demo/erp_data.json` | NetSuite, QuickBooks |
| `bank` | `bank_connector.py` | `data/demo/bank_data.json` | Plaid |
| `trading` | `trading_connector.py` | `data/demo/trading_data.json` | Alpaca, IBKR |
| `news` | `news_connector.py` | `data/demo/news_data.json` | NewsAPI |
| `custom` | `custom_rest_connector.py` | — | User REST mapping |
| `webhook` | `webhook_connector.py` | — | `POST /ingest/{source}` |

## BaseConnector contract

Implement `backend/connectors/base.py`:

- `connect() -> ConnectionStatus`
- `disconnect() -> None`
- `health_check() -> bool`
- `fetch_batch() -> dict` (raw vendor payload)
- `normalize(raw) -> partial SourceData`

## Plugin registration

Place plugins under `backend/connectors/plugins/{vendor}/connector.py` and register via `CONNECTOR_PLUGINS` env.

## Webhook ingest

`POST /ingest/{source}` with headers:

- `X-Nexus-Tenant-Id`
- `X-Nexus-Signature` (HMAC-SHA256 of body)

## Data modes (truthful)

Each connector exposes `data_mode` on `ConnectionStatus`:

| Mode | Meaning |
|------|---------|
| `demo` | `uses_demo_pipeline()` — synthetic JSON |
| `stub` | Live flag off or credentials missing (Plaid/Alpaca) |
| `empty` | Live flag on; vendor API not implemented (CRM/ERP/news) |
| `live` | Live fetch path active (bank/trading when configured) |

`GET /api/v1/connectors` returns `capabilities[]` with `data_mode`, `live_vendor`, and `notes`.

## API

- `POST /api/v1/connect/{source}` — connect (**admin**)
- `GET /api/v1/sources/status` — all connection statuses
- `POST /api/v1/connect/{source}/sync` — manual sync (**analyst**)
- `GET /api/v1/connectors` — types + capabilities
