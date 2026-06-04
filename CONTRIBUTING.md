# Contributing to Nexus AI

Thank you for helping make Nexus AI credible for developers, buyers, and the open-source community.

## Before you start

1. Read [README.md](README.md) — especially **What ships today** vs **Roadmap**.
2. Skim [docs/PRD.md](docs/PRD.md) and [docs/TRD.md](docs/TRD.md) for contracts.
3. Run demo mode locally (`NEXUS_DEMO_MODE=true`) before touching live integrations.

## Development setup

```bash
cp .env.example .env
python -m venv venv && source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python scripts/generate_demo_data.py --seed 42
uvicorn backend.main:app --reload --port 8000
```

Frontend: `cd frontend && npm install && npm run dev`

## Workflow

1. **Plan** — Short note in PR description: problem, approach, test impact.
2. **Small PRs** — One logical change (agent, connector, contract, or UI slice).
3. **Contracts** — Update Pydantic schemas and `frontend/src/types/nexus.ts` together when events change.
4. **Demo stability** — `pytest tests/` must pass with `NEXUS_DEMO_MODE=true`; do not break seeded demo data without updating `scripts/generate_demo_data.py`.
5. **Truth in docs** — If a feature is stubbed, label it **Roadmap** in README/docs; do not imply live vendor support.

## Code standards

| Area | Tool |
|------|------|
| Python lint/format | `ruff check backend tests` |
| Python types | `mypy backend` (optional locally) |
| Tests | `pytest tests/ -q` |
| Frontend | `cd frontend && npm run type-check && npm run lint` |

Conventions: [.cursor/rules/](.cursor/rules/) (backend async-first, typed schemas, structlog).

### Cursor MCP (optional)

GitHub + Context7 are configured in [.cursor/mcp.json](.cursor/mcp.json). Set `GITHUB_TOKEN` (and optionally `CONTEXT7_API_KEY`) in your user environment, then restart Cursor. See [docs/mcp-setup.md](docs/mcp-setup.md).

## Testing expectations

- New agent logic → extend `tests/test_pipeline_e2e.py` or add focused agent tests.
- New API routes → `tests/test_api.py` or dedicated router tests.
- Connectors → `tests/test_connectors.py` with demo fixtures only unless live tests are gated behind env flags.

## Security

- Never commit `.env`, API keys, or customer data.
- Do not log secrets or full webhook payloads in production code paths.
- HMAC ingest secrets belong in environment variables only.

## Pull request checklist

- [ ] `pytest tests/ -q` passes
- [ ] Frontend `npm run type-check` passes (if TS touched)
- [ ] Demo checklist items still hold ([docs/demo_checklist.md](docs/demo_checklist.md))
- [ ] README/docs updated if behavior or env vars changed
- [ ] Live/vendor claims marked **Shipped** vs **Roadmap**

## Areas we need help

- Live connector implementations (Plaid, Alpaca, CRM/ERP) behind `NEXUS_ENABLE_*`
- `LLMClient` production path with timeout, retry, and prompt redaction
- JWT auth replacing header-trust RBAC for production
- OpenTelemetry in `backend/observability/`
- Frontend tests (Playwright) and hardened WebSocket auth

## Questions

Open a GitHub Discussion or issue with the `question` label. For architecture debates, reference TRD section numbers.
