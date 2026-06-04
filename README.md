# Nexus AI

**Multi-agent financial intelligence** — connects CRM, ERP, banking, and trading systems, detects blind spots, runs adversarial simulations, and evolves from feedback.

## Quick start

```bash
python -m venv venv
venv\Scripts\activate   # Windows
pip install -r requirements.txt
python scripts/generate_demo_data.py --seed 42
uvicorn backend.main:app --reload --port 8000
```

Frontend (separate terminal):

```bash
cd frontend && npm install && npm run dev
```

Open http://localhost:3000 — API docs at http://localhost:8000/docs

## Supported integrations

| Source | Demo | Live |
|--------|------|------|
| CRM | ✓ | Salesforce, HubSpot |
| ERP | ✓ | NetSuite, QuickBooks |
| Banking | ✓ | Plaid |
| Trading | ✓ | Alpaca |
| News | ✓ | NewsAPI |
| Custom | Webhook / REST plugin | |

## Architecture

6 agents: **Connector** → Silent Finder → Adversarial Red Team → Traceback → Decision → Evolution

## Environment

Copy `.env.example` to `.env`. Demo mode works without API keys (`NEXUS_DEMO_MODE=true`).

## License

MIT
