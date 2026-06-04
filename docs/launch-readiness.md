# Launch readiness

This document is the **honest** readiness matrix for Nexus AI open core v0.9. It is updated to match code, not marketing copy.

## Capability matrix

| Area | Status | Notes |
|------|--------|-------|
| Six-agent demo pipeline | **Shipped** | Deterministic rules + demo LLM streams |
| Pre-Release Risk Review API | **Shipped** | `POST /api/v1/risk-review/run` — buyer-facing artifact |
| REST API + OpenAPI | **Shipped** | API key / JWT on protected routes |
| WebSocket streaming | **Shipped** | Optional auth via `NEXUS_WS_REQUIRE_AUTH` |
| Demo data generator | **Shipped** | `scripts/generate_demo_data.py --seed 42` |
| Memory (Chroma + NetworkX + SQLite) | **Shipped** | Shared layer; not tenant-isolated |
| Audit hash chain | **Shipped** | `GET /api/v1/audit/verify` |
| HMAC webhook ingest | **Shipped** | Enforced when `NEXUS_DEMO_MODE=false` |
| Live Plaid / Alpaca | **Stub** | Empty or stub fetch without credentials |
| Live CRM/ERP/news vendors | **Missing** | Demo JSON only |
| Live LLM | **Stub** | Wired when demo off + keys |
| Multi-tenant DB isolation | **Missing** | Header-scoped orchestrators only |
| Prometheus / OTel | **Planned** | `backend/observability/` placeholder |
| External alerting | **Stub** | `backend/services/alerting.py` |
| Redis in compose | **Optional** | Profile `prod`; app does not use it |

## Environment tiers

| Tier | Flags | Auth | Data | Purpose |
|------|-------|------|------|---------|
| Local dev | `DEMO=true` | API key + optional `X-Nexus-Role` | Synthetic | Engineering |
| Demo / sales | `DEMO=true` | API key + optional JWT | Synthetic | Judges, investors |
| Pre-live dress rehearsal | `PRE_LIVE=true` | JWT roles only (no trusted headers) | Synthetic | RBAC/HMAC rehearsal |
| Staging | `DEMO=false` | JWT recommended | Sandbox vendors | Integration testing |
| Production | `DEMO=false` | JWT required + gateway RBAC | Live connectors | Pilot customers |

## Demo acceptance criteria

See [demo_checklist.md](demo_checklist.md). Automated minimum:

```bash
python scripts/generate_demo_data.py --seed 42
pytest tests/test_pipeline_e2e.py tests/test_nexus_run_demo.py tests/test_websocket.py -q
```

Manual UI pass: sidebar **WS: connected**, **Run Pipeline** → **COMPLETE**, ≥3 blind spots, traceback graph, decisions + evolution.

## Production acceptance criteria (not met in v0.9)

- [ ] `AUTH_MODE=jwt_required` and `NEXUS_WS_REQUIRE_AUTH=true`
- [ ] Rotated `NEXUS_API_KEY`, `JWT_SECRET`, ingest HMAC secrets (not defaults)
- [ ] `NEXUS_DEMO_MODE=false` with validated live connector + LLM paths
- [ ] TLS termination; **do not** trust client-supplied `X-Nexus-Role` at edge
- [ ] Persistent volumes for `data/chroma`, `data/graph.json`, `data/nexus.db`, `data/audit.jsonl`
- [ ] Security contact in [SECURITY.md](../SECURITY.md) replaced with real address
- [ ] Load test on WebSocket concurrent pipelines (not characterized yet)

## Release checklist (maintainers)

1. `ruff check backend tests`
2. `pytest tests/ -q`
3. `cd frontend && npm run type-check && npm run lint && npm run build`
4. `python scripts/verify_setup.py`
5. Update README **What ships today** if capability status changed
6. Tag release only after CI green on `main`

## Verdict guide

| Verdict | Meaning |
|---------|---------|
| **Not ready** | Cannot run tests or demo; docs contradict code |
| **Demo ready** | Seeded pipeline + dashboard + CI; suitable for evaluation |
| **Pilot ready** | Demo ready + sellable workflow artifact + pre-live auth profile documented |
| **Beta ready** | Pilot ready + live integrations validated in staging |
| **Production ready** | Beta + tenant isolation, observability, security review |

**Current open-core verdict: Pilot ready** (v0.9.1). Demo-ready for investors; **design-partner pilots** supported via Pre-Release Risk Review API + pre-live profile. Not production ready until live data paths and tenancy hardening are complete.

See [GTM_LAUNCH.md](GTM_LAUNCH.md) for ICP, wedge, and sale blockers.

## Market differentiation (code-backed today)

1. **Simulation before action** — Adversarial pass on each blind spot before decisions.
2. **Traceable memory** — Vector/graph/traceback links current signals to prior loss events.
3. **Auditable outputs** — Hash-chained audit log + structured agent events (not a single chat transcript).

Planned differentiation (documented, not shipped): connector plugins, approval workflows, OTel, tenant-isolated stores.
