# Nexus Demo Checklist

- [ ] `python scripts/generate_demo_data.py --seed 42`
- [ ] `uvicorn backend.main:app --reload` — GET /health returns ok
- [ ] GET /api/v1/sources/status with X-Nexus-Key
- [ ] POST /api/v1/nexus/run/demo completes
- [ ] WS /ws/nexus/stream — RUN_PIPELINE yields 6 AGENT_COMPLETE
- [ ] Frontend connections page shows 5 sources
- [ ] 3+ blind spots on dashboard
- [ ] Decisions: trade + loan
- [ ] Evolution +12.3%
