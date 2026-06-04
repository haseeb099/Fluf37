# Deployment

## Docker Compose (local / staging)

```bash
cp .env.example .env
# Ensure demo data exists on host or in image
python scripts/generate_demo_data.py --seed 42
docker compose up --build
```

| Service | Port | Image |
|---------|------|-------|
| api | 8000 | `Dockerfile.api` |
| frontend | 3000 | `frontend/Dockerfile` |
| redis | 6379 | optional `--profile prod` |

### Health checks

- API: `GET /health` (liveness), `GET /ready` (readiness after memory init)
- Compose file uses an HTTP probe against `/health` (Python-based in image)

### Volumes

Mount `./data` to `/app/data` so Chroma, SQLite, graph, and audit survive restarts.

## Production checklist

1. **Secrets** — Set strong `NEXUS_API_KEY`, ingest HMAC secrets, and vendor keys via secret manager (not `.env` in image).
2. **Demo off** — `NEXUS_DEMO_MODE=false` only after live LLM and connectors are implemented and tested.
3. **CORS** — Restrict `CORS_ORIGINS` to your frontend origin(s).
4. **TLS** — Terminate TLS at load balancer; enforce HTTPS to API and WSS.
5. **WebSocket** — Add auth (query token or mTLS) before exposing publicly.
6. **RBAC** — Strip `X-Nexus-Role` from untrusted clients; set at gateway from IdP claims.
7. **Persistence** — Back up `data/nexus.db`, `data/chroma`, `data/graph.json`, `data/audit.jsonl`.
8. **Logging** — Ship structlog JSON to your SIEM; redact PII from prompts and webhook bodies.
9. **Rate limiting** — Wire `slowapi` or edge rate limits (not enabled in app today).
10. **CI** — Mirror `.github/workflows/ci.yml` on release tags.

## Kubernetes (outline)

- Deployment: API with `readinessProbe` → `/ready`, `livenessProbe` → `/health`
- StatefulSet or PVC for `data/`
- Separate Deployment for frontend with `NEXT_PUBLIC_*` aimed at internal API service
- Ingress with WSS support

## Scaling limits (current code)

- Per-process orchestrator map (`_orchestrators`) — horizontal scaling requires sticky sessions or externalized pipeline state (roadmap).
- Shared memory path must be R/W shared filesystem or single replica until memory is externalized.

## Environment matrix

| Environment | `NEXUS_DEMO_MODE` | Data |
|-------------|-------------------|------|
| Local dev | true | `generate_demo_data.py` |
| CI | true | generated in workflow |
| Staging | true or false | synthetic or sandbox vendor keys |
| Production | false (when ready) | Live connectors + vault |
