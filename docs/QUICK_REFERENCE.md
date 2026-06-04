# NEXUS AI — Cursor Quick Reference
## The 10 Most Important Prompts (Bookmark This)

---

## 🏁 START HERE (Open in Cursor, paste in Chat)

### 0. Orientation Prompt (Run this FIRST in every new Cursor session)
```
I'm building NEXUS AI from the docs in this repo. 

Please read these files in order:
1. .cursor/rules/nexus.mdc (project rules — CRITICAL)
2. docs/SE.md (system engineering spec)
3. docs/TRD.md (technical requirements)

Then confirm you understand the architecture: 6 agents (Connector, Silent Finder, Adversarial Red Team, Traceback, Decision, Evolution), streaming via WebSocket, Pydantic v2 schemas, demo mode that works without API keys.

Tell me the current state of the codebase (what exists, what's missing) then ask me which phase to start.
```

---

## ⚡ FAST TRACK (If you want to build one thing quickly)

### Build the entire backend in one shot:
```
Read .cursor/rules/nexus.mdc, docs/SE.md, and docs/TRD.md.

Build the complete NEXUS AI Python backend in this order:
1. backend/schemas/models.py — all Pydantic v2 schemas
2. backend/config.py — NexusConfig with pydantic-settings
3. backend/utils/llm_client.py — Anthropic + fallback + streaming
4. backend/utils/audit_log.py + errors.py
5. backend/memory/ — vector.py, graph.py, timeseries.py, layer.py
6. backend/agents/base.py — BaseAgent abstract class
7. backend/agents/silent_finder.py
8. backend/agents/adversarial.py
9. backend/agents/traceback.py
10. backend/agents/decision.py
11. backend/agents/evolution.py
12. backend/agents/orchestrator.py
13. backend/main.py — FastAPI app

Use demo mode everywhere (NEXUS_DEMO_MODE=true). The demo must work with no API keys.
Generate complete files, no stubs or TODOs.
```

### Build the entire frontend in one shot:
```
Read .cursor/rules/nexus.mdc and docs/TRD.md sections 4 and 5.

Build the complete NEXUS AI Next.js 14 frontend:
1. frontend/src/types/nexus.ts — TypeScript interfaces mirroring Pydantic schemas
2. frontend/src/store/nexusStore.ts — Zustand store with all actions
3. frontend/src/hooks/useNexusWebSocket.ts — auto-reconnect WS hook
4. frontend/src/lib/api.ts + utils.ts
5. frontend/src/app/globals.css — Obsidian Intelligence design system
6. frontend/src/app/layout.tsx — root layout with providers
7. All pages: dashboard, agents, traceback, decisions, evolution
8. All components: AgentGrid, StreamingText, TraceGraph, ConfidenceMeter, etc.

Use the design tokens from TRD (dark theme, agent colors, CSS variables).
Every component must be typed with TypeScript strict mode.
```

---

## 🔧 FIX-IT PROMPTS

### When streaming isn't working:
```
The WebSocket streaming isn't working correctly. 

Review:
1. backend/agents/base.py — the _stream_llm() method
2. backend/agents/orchestrator.py — how it broadcasts events
3. frontend/src/hooks/useNexusWebSocket.ts — message handling
4. frontend/src/store/nexusStore.ts — handleWSEvent action

The flow should be: LLM token → AgentEvent(AGENT_TOKEN) → WS broadcast → nexusStore.agentTokens[agent_id] += token → StreamingText component updates

Find and fix the disconnect.
```

### When Pydantic validation is failing:
```
I'm getting Pydantic validation errors. 

Review backend/schemas/models.py and check:
1. Are all Optional fields actually optional (have defaults)?
2. Are all datetime fields using datetime type (not str)?
3. Do the SignalWeights validators allow the actual values being passed?
4. Are all Literal types exhaustive?

Also check if the agent creating the invalid output is using model_validate() correctly.

Show me the specific validation error and fix the schema or the agent output.
```

### When demo mode isn't working:
```
Demo mode should work with zero API keys. Check:
1. backend/config.py — is NEXUS_DEMO_MODE loading from env correctly?
2. backend/utils/llm_client.py — does it return synthetic responses when demo=True?
3. Each agent's run_demo() method — does it return hardcoded outputs?
4. backend/utils/synthetic_data.py — does it load from data/demo/*.json?

Fix any agent that makes a real LLM call when demo_mode=True.
```

---

## 🎯 FEATURE ADD PROMPTS

### Add a new blind spot type:
```
Add a new blind spot type to the Silent Forcing Finder: "Vendor Concentration Risk"

It should detect when a single vendor receives >30% of total payments.

Update:
1. backend/agents/silent_finder.py — add detection logic in identify_gaps()
2. data/demo/bank_data.json — add transactions that would trigger it
3. docs/TRD.md — add to hidden patterns table
4. frontend/src/components/dashboard/BlindSpotCard.tsx — show vendor concentration icon

The new blind spot should appear in demo mode with severity "high".
```

### Add a new agent:
```
Add a 7th agent: "ComplianceAgent" that checks regulatory requirements.

Following the patterns in docs/SE.md:
1. Create backend/agents/compliance.py — ComplianceAgent class
2. Update backend/schemas/models.py — add ComplianceOutput schema
3. Update backend/agents/orchestrator.py — add to pipeline (runs after decision)
4. Update frontend/src/types/nexus.ts — add "compliance" to AgentId type
5. Update frontend/src/store/nexusStore.ts — add compliance to agent states
6. Add a compliance card to the dashboard

The agent should check: sanctions lists, AML red flags, regulatory thresholds.
In demo mode: flag the circular payment as AML concern.
```

---

## 🚨 EMERGENCY PROMPTS

### If the backend won't start:
```
The backend isn't starting. Run these checks:
1. Are all imports resolvable? (check for circular imports)
2. Is the FastAPI lifespan function correct syntax for FastAPI 0.110+?
3. Are all async functions properly awaited?
4. Is the WebSocket manager initialized before first use?

Show me the full error traceback and fix the root cause.
```

### If the frontend won't compile:
```
The frontend has TypeScript errors. Run:
cd frontend && npx tsc --noEmit

Show all errors and fix them. Common issues:
- nexusStore.ts missing action signatures
- WSEvent type not covering all message types
- React Flow node types not matching custom node interfaces
- Recharts data shape not matching component props
```

### Final demo check:
```
Run a complete sanity check before the demo:

1. Does the backend start cleanly on port 8000?
2. Does GET /health return {"status": "ok"}?
3. Does GET /docs show all API endpoints?
4. Does POST /api/v1/nexus/run/demo return 202?
5. Does WS /ws/nexus/stream accept connections?
6. Does a full demo pipeline run produce 6 AGENT_COMPLETE events?
7. Does the frontend connect to WS on load?
8. Does clicking "Run Pipeline" trigger all 6 agents?
9. Does the Traceback graph render with nodes?
10. Does the Evolution page show +12.3% improvement?

Fix any failures. The demo MUST complete in under 6 minutes.
```
