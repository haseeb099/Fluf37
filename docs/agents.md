# Six-agent pipeline

Status labels: **Shipped** (demo + tests), **Stub** (wired, not production-complete), **Planned**.

The orchestrator (`backend/agents/orchestrator.py`) runs agents **sequentially**. Each agent implements `BaseAgent.run()` and yields typed `AgentEvent` messages. Pipeline states: `IDLE` → `CONNECTING` → `ANALYZING` → `ATTACKING` → `TRACING` → `DECIDING` → `EVOLVING` → `COMPLETE` (or `ERROR`).

| Agent ID | Class | Input | Output | Failure mode |
|----------|-------|-------|--------|--------------|
| `connector` | `ConnectorAgent` | — | `ConnectorOutput` | No `AGENT_COMPLETE` → pipeline `ERROR` |
| `silent_finder` | `SilentForcingFinder` | `SourceData` | `BlindSpotOutput` | Timeout → `AGENT_ERROR` |
| `adversarial` | `AdversarialRedTeam` | `BlindSpotOutput` | `AttackOutput` | Timeout / empty library edge cases |
| `traceback` | `TracebackAgent` | `AttackOutput` | `TracebackOutput` | Memory search miss → empty matches (non-fatal) |
| `decision` | `DecisionAgent` | `AllSignals` | `DecisionOutput[]` | Rule-based decisions; persisted to SQLite |
| `evolution` | `EvolutionAgent` | `EvolutionInput` | `EvolutionReport` | `approval_required=true` (weights not auto-applied) |

## Connector agent — **Shipped** (demo)

- Syncs enabled sources via `ConnectionManager` (`demo=True` reads `data/demo/*.json`).
- Merges partial data into normalized `SourceData` through per-connector `normalize()`.
- Live fetch: **Stub** when `NEXUS_ENABLE_*` is true but vendor credentials are missing (returns empty batch with warning).

## Silent Forcing Finder — **Shipped** (demo rules + streamed narrative)

- **Deterministic** blind spots from cross-source rules in `_detect_demo_patterns()` (CRM/ERP overlap, cash-flow timing, circular payments, order-book/RSI divergence, vendor concentration).
- Streams canned LLM text via `LLMClient` in demo mode (not live model reasoning).
- Stores output in vector memory for traceback.

## Adversarial Red Team — **Shipped** (demo)

- Builds one `Attack` per blind spot using `data/attack_library/v1.json` templates.
- Demo mode streams a single red-team narrative; live mode would stream per blind spot (**Stub** until `LLMClient` live path is validated in production).

## Traceback — **Shipped** (demo)

- Vector + graph search over historical incidents seeded in `MemoryLayer.initialize_demo()`.
- Graph nodes use **titles** and **affected_entities** (e.g. “Circular payment loop — Acme Corp”), not raw `fail_001` IDs.
- Paths and blast radius come from `NexusGraph.find_paths()` / `get_blast_radius()` on the matched failure id.

## Decision — **Shipped** (demo rules)

- Trade and credit recommendations from deterministic rules on `SourceData` + prior agent outputs.
- Records each decision in SQLite time-series for evolution feedback.

## Evolution — **Shipped** (demo report; approval gate)

- Produces `EvolutionReport` with proposed weight deltas and new rules.
- `approval_required=True` — no automatic weight application in v0.9.
- Admin approval UI: **Planned** (see [roadmap.md](roadmap.md)).

## LLM usage

| Mode | Behavior |
|------|----------|
| `NEXUS_DEMO_MODE=true` | `LLMClient` streams agent-scoped canned text; audit log records token counts |
| Demo off + API keys | Live Anthropic/OpenAI path (**Stub** — requires ops validation) |

## Contracts

All payloads are Pydantic models in `backend/schemas/models.py`. Frontend mirrors: `frontend/src/types/nexus.ts`, validated on WebSocket receive via `frontend/src/lib/wsSchema.ts`.

## Audit trace

Each pipeline run gets a `correlation_id` on `PIPELINE_STATE` events. `PipelineTracer` appends `pipeline_start`, `pipeline_state`, `agent_complete`, and `pipeline_complete` rows to `data/audit.jsonl` (hash-chained). Inspect via `GET /api/v1/audit/recent` (analyst+).

## Testing

- Full pipeline: `tests/test_pipeline_e2e.py`
- RBAC / pre-live: `tests/test_rbac.py`
- Pipeline audit: `tests/test_pipeline_trace.py`
- HTTP demo run: `tests/test_nexus_run_demo.py`
- WebSocket: `tests/test_websocket.py`
- Agent timeout: `tests/test_orchestrator_timeout.py`
