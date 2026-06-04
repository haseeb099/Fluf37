# Nexus AI — Connector & Plugin API

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

## API

- `POST /api/v1/connect/{source}` — connect
- `GET /api/v1/sources/status` — all connection statuses
- `POST /api/v1/connect/{source}/sync` — manual sync
