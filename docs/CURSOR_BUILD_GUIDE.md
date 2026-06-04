# NEXUS AI — Cursor Build Guide
## Complete Prompt Sequence to Build the Entire Project

---

## ⚡ BEFORE YOU START

1. Open the `nexus-ai/` folder in Cursor
2. Cursor will auto-detect `.cursor/rules/nexus.mdc` — this is your AI rulebook
3. Open Cursor Chat (⌘L) and paste prompts below **in order**
4. After each prompt: review the file, then move to the next
5. Always use **Claude Sonnet** as your Cursor model for best results

---

## 🚀 PHASE 1 — Project Foundation (Day 1, ~2 hours)

### Prompt 1.1 — Schemas (START HERE, everything depends on this)
```
Read docs/SE.md section 3 (Pydantic Schemas) and docs/TRD.md section 3.

Generate the complete backend/schemas/models.py file containing ALL Pydantic v2 schemas for NEXUS AI:
- SourceData (with CRMDeal, BankTransaction, TradingPosition, NewsItem)
- BlindSpot, BlindSpotOutput
- Attack, AttackOutput, AttackLibrary
- FailureRecord, TracebackResult, TimelineEvent
- DecisionOutput, SignalWeights, AllSignals
- EvolutionReport, EvolutionCycle
- AgentEvent, AgentState (enum)
- ConnectorOutput, ConnectorStatus
- NexusReport (final aggregated output)
- MemoryResult, MemoryStats, MemoryMetadata
- AuditEntry, AuditVerification

Requirements:
- Pydantic v2 syntax (model_config, model_validator, Field)
- All fields typed, no Optional without reason
- Add validators where logical (weights sum to 1.0, confidence 0-1, etc.)
- Add model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})
- Use Literal types not enums for severity/state
- Include docstrings on each class
```

---

### Prompt 1.2 — Config
```
Read docs/SE.md section 7 and .env.example.

Generate backend/config.py with NexusConfig using pydantic-settings:
- All settings from SE.md section 7
- Load from .env with python-dotenv
- Type-safe, with Field(env="VAR_NAME") for each env variable
- Add a get_config() singleton function (lru_cache)
- Include a NexusConfig.is_demo() helper method
- Include docstring explaining each setting group
```

---

### Prompt 1.3 — LLM Client
```
Generate backend/utils/llm_client.py — the unified LLM wrapper for NEXUS AI.

Requirements:
- AsyncAnthropic as primary (claude-3-5-sonnet-20241022)
- AsyncOpenAI as fallback
- async stream() method: AsyncIterator[str] — yields tokens one by one
- async complete() method: returns full string
- Retry logic: 3x with exponential backoff using tenacity
- Automatic fallback to OpenAI on 3rd failure
- In demo mode: returns pre-seeded streaming responses (no real API call)
- Audit log call after each completion (agent_id, model, tokens, latency_ms)
- Structured logging with structlog
- All timeouts respect NexusConfig.agent_timeout_seconds
- Never expose raw exceptions — wrap in NexusError.LLMError
```

---

### Prompt 1.4 — Audit Log + Error Hierarchy
```
Generate two files:

1. backend/utils/audit_log.py:
- AuditLog class with append-only write to audit.jsonl
- Hash chain: sha256(entry_json + prev_hash)
- verify() method: re-computes all hashes, returns first tamper
- export(format: "json"|"pdf") → bytes
- Structured entry: timestamp, agent_id, action, payload_preview (truncated), tokens, latency, model, hash

2. backend/utils/errors.py:
- NexusError base with: message, agent_id, recoverable, timestamp
- AgentError subclass
  - LLMError (has: model, retry_count)
  - TimeoutError (has: agent_id, elapsed_seconds)  
  - SchemaError (has: field_errors)
- ConnectorError subclass
  - AuthError (has: source_name)
  - DataError (has: source_name, raw_error)
- MemoryError subclass
  - StorageError

All errors should log themselves on creation using structlog.
```

---

### Prompt 1.5 — Synthetic Data Generator
```
The file scripts/generate_demo_data.py already exists. 

Now generate backend/utils/synthetic_data.py — a Python module that:
- Loads the generated JSON files from data/demo/
- Returns typed SourceData (Pydantic model from schemas/models.py)
- Has get_demo_source_data() → SourceData
- Has get_demo_crm(), get_demo_bank(), get_demo_trading(), get_demo_news() separately
- Pre-populates demo ChromaDB memory with 3 historical failure records
- Pre-populates demo graph with 5 nodes and 4 edges (historical failures)
- All seeded from NexusConfig.demo_seed for reproducibility
```

---

## 🧠 PHASE 2 — Memory Layer (Day 1, ~1 hour)

### Prompt 2.1 — Vector Memory
```
Generate backend/memory/vector.py — ChromaDB vector memory wrapper.

Requirements:
- VectorMemory class
- Uses chromadb.EphemeralClient() in demo mode, chromadb.PersistentClient(path) in prod
- Embedding: sentence_transformers all-MiniLM-L6-v2 (works offline, no API key)
- Collection name: "nexus_failures"
- async store(text, metadata: MemoryMetadata) → doc_id (str)
- async search(query, n_results=5, filter=None) → List[MemoryResult]
- async delete(doc_id) → None
- async get_stats() → MemoryStats
- async deduplicate(threshold=0.95) → int (removed count)
- Initialize with 3 pre-seeded historical failures in demo mode
- All methods handle errors gracefully, log with structlog
```

---

### Prompt 2.2 — Graph Memory
```
Generate backend/memory/graph.py — NetworkX graph memory wrapper.

Requirements:
- NexusGraph class wrapping networkx.DiGraph
- Node types: "failure", "blind_spot", "attack", "loss_event"
- Edge types: "leads_to", "similar_to", "exploits", "prevented_by"
- add_node(id, type, data: dict) → None
- add_edge(source, target, type, probability, timestamp) → None
- find_paths(source_id, target_type="loss_event", max_hops=7) → List[List[str]]
- get_blast_radius(node_id, max_depth=3) → Set[str]
- get_subgraph(node_ids: List[str]) → dict (JSON-serializable for React Flow)
- serialize() → dict, deserialize(data) → None
- save(path: str) and load(path: str)
- Initialize with demo historical graph in demo mode
- All node/edge attribute access is type-safe
```

---

### Prompt 2.3 — Time Series Memory + MemoryLayer Facade
```
Generate two files:

1. backend/memory/timeseries.py:
- TimeSeriesMemory using SQLite (aiosqlite)
- Create tables on init: agent_metrics, decisions, evolution_cycles (see TRD section 4.3)
- async record_agent_run(agent_id, tokens, latency_ms, success, model) → None
- async record_decision(decision: DecisionOutput) → None
- async record_evolution(cycle: EvolutionCycle) → None
- async get_decisions(days=7, outcome_filter=None) → List[DecisionOutput]
- async get_agent_metrics(agent_id=None, days=7) → pd.DataFrame
- async update_decision_outcome(decision_id, outcome) → None

2. backend/memory/layer.py:
- MemoryLayer class combining all three memory types
- async store_agent_output(agent_id, output: BaseModel, text_repr: str) → None
- async search(query, n=5) → List[MemoryResult]
- async get_graph() → NexusGraph
- async get_stats() → dict (combined stats from all three)
- Delegate to underlying stores; handle failures gracefully
```

---

## ⚙️ PHASE 3 — Agents (Day 2, ~4 hours)

### Prompt 3.1 — BaseAgent
```
Generate backend/agents/base.py — the abstract base all agents inherit from.

Requirements:
- BaseAgent abstract class
- ClassVar[str] agent_id — must be defined by subclasses
- AgentState enum (WAITING, DISPATCHED, RUNNING, STREAMING, COMPLETE, ERROR)
- AgentEvent Pydantic model (type, agent_id, data, timestamp)
- __init__(config, memory, llm_client)
- @abstractmethod async run(payload) → AsyncIterator[AgentEvent]
- async run_demo() → AsyncIterator[AgentEvent] — default raises NotImplementedError
- Helper _emit(type, data) → AgentEvent
- Helper _stream_llm(prompt, system, temperature) → AsyncIterator[str]
  - Uses llm_client.stream()
  - Emits AGENT_TOKEN events for each token
  - Wraps in try/except → emits AGENT_ERROR on failure
- state property and _set_state() method
- Automatic state transitions: WAITING → DISPATCHED → RUNNING → STREAMING → COMPLETE
```

---

### Prompt 3.2 — Silent Forcing Finder Agent
```
Read docs/SE.md section 2.5 and docs/TRD.md section 3.2 carefully.

Generate backend/agents/silent_finder.py — the SilentForcingFinder agent.

This agent statistically infers what the user is NOT measuring.

Algorithm (implement fully, not as stubs):
1. compute_metric_coverage(data: SourceData) → MetricMatrix
   - Extract all measurable fields from CRM, bank, trading, news
   - Return matrix: {source: [available_metrics]}
   
2. mutual_information_score(matrix) → MIMatrix  
   - Compute pair-wise relationships between cross-source metrics
   - Use correlation coefficient as proxy for MI in demo
   - Return: {(metric_a, metric_b): score, p_value}
   
3. identify_gaps(mi_matrix) → List[Gap]
   - Find high-MI pairs where one variable has no monitoring rule
   - Return gaps with estimated impact scores
   
4. llm_hypothesize(gaps) → List[BlindSpot] [STREAMING via _stream_llm]
   - System prompt: "You are a financial risk analyst. Identify what is NOT being measured..."
   - Stream LLM response as tokens
   - Parse final output into List[BlindSpot]
   
5. score_severity(blind_spots) — apply thresholds from TRD section 3.2
6. counterfactual_reasoning(blind_spots) — "If tracked, would have caught..."

In demo mode: inject the 7 known hidden patterns as blind spots + add LLM reasoning.

run_demo() must return the known synthetic blind spots from synthetic data.
```

---

### Prompt 3.3 — Adversarial Red Team Agent
```
Read docs/SE.md section 2.6 and docs/TRD.md section 3.3 carefully.

Generate backend/agents/adversarial.py — the AdversarialRedTeam agent.

This agent tries to break every blind spot it's given.

ReAct loop (implement fully):
for blind_spot in blind_spots:
    history = []
    for iteration in range(max_iterations=5):
        # REASON [STREAMING]
        thought = await llm.stream("Given blind spot X and history Y, what's the logical gap in current detection rules?")
        
        # ACT [STREAMING]  
        action = await llm.stream("Generate a specific attack scenario exploiting gap: {thought}")
        
        # OBSERVE [rule-based, no LLM needed]
        observation = _evaluate_attack(action, current_rules)  # deterministic scoring
        
        history.append(ReActStep(thought, action, observation))
        if observation.success_probability > 0.7:
            break
    
    best_attack = max(history, key=lambda s: s.observation.success_probability)
    defense = await llm.complete("Generate a specific detection rule to prevent: {best_attack}")
    attacks.append(Attack(..., proposed_defense=defense))

Also implement:
- async stress_test(recommendation: DecisionOutput) → StressTestResult
- async update_library(new_attacks: List[Attack]) → None
- _evaluate_attack() — deterministic scoring function (no LLM), checks against known rule patterns

Attack library: load from data/attack_library/v{latest}.json on init.
In demo mode: return known attacks for the 7 hidden patterns.
```

---

### Prompt 3.4 — Traceback Agent
```
Read docs/SE.md section 2.7 and docs/TRD.md section 3.4 carefully.

Generate backend/agents/traceback.py — the TracebackAgent.

RAG + Graph pipeline (implement fully):
1. embed(pattern_description) → vector
   - Use memory.vector.embedding_fn directly
   
2. search(vector, n=5) → similar_docs
   - Include metadata filter: resolved=False, severity in [critical, high]
   
3. build_subgraph(similar_docs) → NetworkX subgraph
   - Extract node IDs from similar docs metadata
   - Get subgraph from memory.graph
   
4. find_paths(subgraph) → List[Path]
   - BFS from each similar node toward "loss_event" nodes
   - Score each path: product of edge probabilities
   - Sort by score, take top 3
   
5. score_paths(paths) → annotated paths with confidence
   
6. llm_synthesize(top_paths, similar_docs) [STREAMING]
   - "Given these historical failures and current pattern, synthesize: what is likely to happen?"
   
7. estimate_blast_radius(matched_nodes) → List[str]
   - BFS 3 hops from each matched node
   - Return all connected asset IDs

Also implement:
- async store_failure(failure: FailureRecord) → None (stores in both vector + graph)
- async get_blast_radius(node_id) → BlastRadius

In demo mode: return pre-seeded traceback showing the March 2026 circular payment incident.
```

---

### Prompt 3.5 — Decision Agent
```
Read docs/SE.md section 2.8 and docs/TRD.md section 3.5 carefully.

Generate backend/agents/decision.py — the DecisionAgent.

Mixture of Experts (implement fully):

Each expert is a class method:
- _analyze_technical(trading: List[TradingPosition]) → ExpertSignal
  - Check: RSI, MACD, order book imbalance, volume anomalies
  - Returns: (recommendation, confidence, reasoning)
  
- _analyze_fundamental(crm: List[CRMDeal]) → ExpertSignal
  - Check: deal health, payment term mismatches, customer concentration
  - Returns: (recommendation, confidence, reasoning)
  
- _analyze_news(news: List[NewsItem]) → ExpertSignal
  - Check: sentiment score, named entity matches, fraud-related headlines
  - Returns: (recommendation, confidence, reasoning)
  
- _analyze_forcing(blind_spots: List[BlindSpot], attacks: List[Attack]) → ExpertSignal
  - This is Nexus's unique edge
  - High severity blind spots with high attack success → negative signal
  - Returns: (recommendation, confidence, reasoning)

Aggregation:
  weighted_score = Σ(w_i × conf_i × rec_i) / Σ(w_i)
  # Load weights from SQLite (evolution history), default to SignalWeights()

Adversarial check:
  stress_result = await adversarial_agent.stress_test(proposed_recommendation)

Sensitivity analysis:
  For each signal: ∂(score)/∂(w_i) — numerical approximation

LLM synthesis [STREAMING]:
  "Given these expert signals [breakdown], adversarial test [result], synthesize the final decision..."

Output: DecisionOutput with full signal_breakdown, sensitivity, adversarial_stress_passed

In demo mode: 
  - Trade decision for ACME (SELL — order book imbalance + news)
  - Loan decision for Acme Corp deal (REVIEW — payment terms mismatch + CFO overlap)
```

---

### Prompt 3.6 — Evolution Agent
```
Read docs/SE.md section 2.9 and docs/TRD.md section 3.6 carefully.

Generate backend/agents/evolution.py — the EvolutionAgent.

Weekly cycle (implement fully):
1. load_decisions(days=7) — from memory.timeseries
2. load_outcomes() — only decisions with submitted outcomes
3. compute_rewards: correct=+1, incorrect=-1, no_feedback=0
4. update_weights:
   w_new = clip(w_old + lr * Σ(reward × signal_contribution), 0.05, 0.60)
   Renormalize so weights sum to 1.0
5. Overfitting check: if false_positive_rate > 0.3 → halve learning rate
6. Regime detection: if last 3 decisions all wrong → flag "distribution shift"
7. propose_attack_library_additions (from near-miss patterns)
8. propose_detection_rules (from successful traceback paths)
9. backtest(new_weights) — re-score past 7-day decisions with new weights
10. Generate EvolutionReport [STREAMING via _stream_llm]
11. Store as pending update — DO NOT auto-apply

Also implement:
- async apply_approved_update(update) — only called after human approval
- async detect_regime_shift() → Optional[RegimeShiftWarning]
- async backtest(new_weights) → BacktestResult

In demo mode: return pre-computed report showing +12.3% self-improvement week-over-week.
```

---

### Prompt 3.7 — Orchestrator
```
Generate backend/agents/orchestrator.py — the NexusOrchestrator.

This is the conductor of all agents.

Requirements:
- NexusOrchestrator class
- async run_pipeline(source_data, mode="demo"|"live") → AsyncIterator[AgentEvent]
  Pipeline order (with proper dependency handling):
  1. connector — gather all source data
  2. silent_finder — analyze source data for blind spots
  3. adversarial — attack each blind spot (can parallelize per blind spot)
  4. traceback — RAG + graph for each attack
  5. decision — aggregate all signals
  6. evolution — background task, doesn't block response

- async dispatch(agent_id, payload) → AsyncIterator[AgentEvent]
  - Apply timeout: asyncio.wait_for(agent.run(payload), timeout=config.agent_timeout_seconds)
  - On timeout: yield partial output + warning AgentEvent
  - Store output in OrchestratorContext after completion

- WebSocketManager integration:
  - All yielded events broadcast to all connected WebSocket clients

- OrchestratorContext: TypedDict with all agent outputs

- Pipeline state machine: emit PIPELINE_STATE events as state transitions

- async aggregate_results() → NexusReport

- Graceful degradation: if any non-critical agent fails, continue with available data
```

---

## 🌐 PHASE 4 — FastAPI Backend (Day 2, ~1 hour)

### Prompt 4.1 — Main FastAPI App
```
Generate backend/main.py — the complete FastAPI application.

Requirements:
- FastAPI app with lifespan context manager
  - on_startup: init config, agents, memory layer, load demo data
  - on_shutdown: flush memory, close DB connections
  
- CORS middleware: allow origins from config.cors_origins
- Structured logging middleware (log every request: method, path, status, latency)
- API key auth dependency: check X-Nexus-Key header

- Include routers:
  - /api/v1/nexus/* — pipeline endpoints
  - /api/v1/agents/* — individual agent endpoints
  - /api/v1/memory/* — memory search/stats
  - /api/v1/decisions/* — decisions + outcome submission
  - /api/v1/evolution/* — evolution report + trigger
  - /ingest/* — webhook ingestion

- WebSocket endpoint /ws/nexus/stream:
  - Accept connection
  - Validate WS messages with Pydantic
  - On "RUN_PIPELINE": run orchestrator.run_pipeline() and stream all events
  - Auto-reconnect support (don't crash on client disconnect)
  - Heartbeat: respond to PING with PONG

- GET /health — returns {"status": "ok", "demo_mode": bool, "agents": {agent_id: state}}

- All endpoints return proper HTTP status codes with error detail
- Use dependency injection for: config, orchestrator, memory layer
```

---

### Prompt 4.2 — API Routers
```
Generate the API router files (put in backend/routers/):

1. nexus.py:
   POST /run — run full pipeline, returns 202 Accepted + pipeline_id
   POST /run/demo — run with synthetic data
   GET /status — pipeline state

2. agents.py:
   POST /{agent_id}/run — run single agent
   GET /status — all agent states + last run time

3. memory.py:
   GET /search?q=...&n=5 — semantic search
   GET /graph — full graph JSON (nodes + edges for React Flow)
   GET /stats — size, oldest entry, etc.

4. decisions.py:
   GET / — paginated decisions list
   GET /{id} — single decision
   POST /{id}/outcome — body: {"outcome": "correct"|"incorrect"}

5. evolution.py:
   GET /report — latest EvolutionReport
   POST /run — trigger manual cycle
   POST /approve/{cycle_id} — approve + apply weight update

All routers: use FastAPI Depends for auth, proper response models, OpenAPI docstrings.
```

---

## 🎨 PHASE 5 — Frontend (Day 3, ~4 hours)

### Prompt 5.1 — TypeScript Types + Zustand Store
```
Generate two files:

1. frontend/src/types/nexus.ts:
- Mirror ALL Pydantic schemas as TypeScript interfaces
- Use exact same field names as Python models
- Add: AgentId = "connector" | "silent_finder" | "adversarial" | "traceback" | "decision" | "evolution"
- Add: WSEvent discriminated union (all message types)
- Add: PipelineState = "IDLE" | "CONNECTING" | ... (all states)

2. frontend/src/store/nexusStore.ts:
- Zustand store with all state from TRD section 4.3
- Actions:
  - startPipeline() — sets state to CONNECTING, sends WS message
  - handleWSEvent(event: WSEvent) — routes to correct handler
  - handleAgentToken(agent_id, token) — appends to agentTokens buffer
  - handleAgentComplete(agent_id, output) — stores in agentOutputs, parses domain data
  - handlePipelineState(state) — updates pipelineState
  - resetPipeline() — clears all state back to IDLE
  - submitOutcome(decisionId, outcome) — POST to API, update local state
- Use immer middleware for immutable state updates
- Add devtools middleware
```

---

### Prompt 5.2 — WebSocket Hook + API Client
```
Generate two files:

1. frontend/src/hooks/useNexusWebSocket.ts:
- useNexusWebSocket(url: string)
- Auto-reconnect with exponential backoff (1s, 2s, 4s, ... max 30s)
- Validate every incoming message with Zod WSEventSchema
- On valid message: call nexusStore.handleWSEvent()
- Heartbeat ping every 30s, detect dead connections
- Buffer messages during reconnect (replay on reconnect)
- Return: { isConnected, connectionState, send, lastEvent, reconnectCount }
- Handle: browser tab visibility changes (pause/resume heartbeat)

2. frontend/src/lib/api.ts:
- Typed API client for all REST endpoints
- Uses fetch with proper error handling
- runPipeline(mode: "demo"|"live") → Promise<{pipeline_id}>
- getAgentStatuses() → Promise<Record<AgentId, AgentStatus>>
- searchMemory(query: string) → Promise<MemoryResult[]>
- getDecisions() → Promise<DecisionOutput[]>
- submitOutcome(id, outcome) → Promise<void>
- getEvolutionReport() → Promise<EvolutionReport>
- getMemoryGraph() → Promise<GraphData>  // for React Flow
All methods: include error handling, return typed responses
```

---

### Prompt 5.3 — Design System + Layout
```
Generate these files using the Obsidian Intelligence design system from TRD section 4.5:

1. frontend/src/app/globals.css:
- All CSS variables from TRD (bg spectrum, accents, agent colors, severity, typography)
- Base styles: html/body dark background, font setup
- Utility classes: .glass-panel (backdrop-blur + border), .agent-glow-{name}
- Scrollbar styling (dark, thin)
- Animation keyframes: pulse-glow, stream-cursor, status-blink

2. frontend/src/lib/utils.ts:
- cn() using clsx + tailwind-merge
- formatCurrency(n) → "$X,XXX"
- formatConfidence(n) → "68%"
- formatTimestamp(iso) → "2 min ago"
- getSeverityColor(severity) → CSS variable string
- getAgentColor(agentId) → CSS variable string

3. frontend/src/app/layout.tsx:
- Root layout with Sidebar + main content area
- WebSocket provider (initialize useNexusWebSocket)
- QueryClientProvider for TanStack Query
- Font loading: Space Grotesk, JetBrains Mono, DM Sans (Google Fonts)
- Dark background: var(--bg-void)

4. frontend/src/components/layout/Sidebar.tsx:
- Navigation links to all 5 pages
- Real-time agent status dots (green/amber/red) per agent — from nexusStore
- "Run Pipeline" button at top — triggers startPipeline()
- Memory size indicator at bottom
- Collapsed/expanded state
```

---

### Prompt 5.4 — Dashboard Page + Agent Grid
```
Generate the main dashboard:

1. frontend/src/app/page.tsx:
- Server component wrapper
- Shows: AgentGrid, PipelineFlow, MetricsPanel, recent BlindSpotCard list

2. frontend/src/components/dashboard/AgentGrid.tsx:
- 6 agent cards in a 2×3 or 3×2 grid
- Each card: agent name, colored border (var(--agent-{name})), status badge
- Streaming text preview (last 100 chars of agentTokens[agent_id])
- Animated glow ring when agent is RUNNING/STREAMING state
- Click to expand → shows full output

3. frontend/src/components/dashboard/PipelineFlow.tsx:
- Visual pipeline: 6 nodes connected by arrows
- Animate: current active agent pulses, completed agents stay lit
- Use SVG or Framer Motion for the animation
- Shows pipeline state label

4. frontend/src/components/shared/StreamingText.tsx:
- Typewriter effect: appends one character at a time
- Blinking cursor at end while streaming
- Smooth scroll to bottom as text grows
- Props: text, isStreaming, className

5. frontend/src/components/shared/SeverityBadge.tsx:
- Pill badge with severity color
- Animated pulse for "critical"

6. frontend/src/components/agents/AgentStatusBadge.tsx:
- Animated status indicator
- RUNNING: spinning ring
- STREAMING: pulsing dot
- COMPLETE: solid green
- ERROR: red with shake animation
```

---

### Prompt 5.5 — Traceback Graph Page
```
Generate the traceback visualization:

1. frontend/src/app/traceback/page.tsx:
- "use client" page
- Loads graph data from API on mount
- Shows TraceGraph + FailureTimeline side by side

2. frontend/src/components/traceback/TraceGraph.tsx:
- React Flow graph with custom node types
- Node types:
  - FailureNode: dark red background, failure icon
  - BlindSpotNode: amber background, warning icon  
  - AttackNode: red/orange, attack icon
  - LossEventNode: critical red, $$$ icon
- Edge types: animated dashed for "leads_to", solid for "similar_to"
- Pan/zoom enabled
- On node click: show detail panel
- Minimap in corner
- Layout: dagre automatic layout (install @dagrejs/dagre)
- Loading skeleton while fetching

3. frontend/src/components/traceback/FailureTimeline.tsx:
- Chronological list of failure records
- Each item: timestamp, severity badge, description, dollar loss
- Hover: highlights connected nodes in graph
```

---

### Prompt 5.6 — Decisions Page + Evolution Page
```
Generate the decisions and evolution pages:

1. frontend/src/app/decisions/page.tsx + components/decisions/:
- DecisionsList: shows all decisions with type, recommendation, confidence
- TradeDecision.tsx: shows ACME SELL signal with signal breakdown bar chart
- LoanDecision.tsx: shows Acme Corp loan REVIEW with risk factors
- ConfidenceMeter.tsx: animated arc gauge (SVG) showing confidence 0-100%
- SensitivityChart.tsx: horizontal bar chart of signal contributions using Recharts
- Outcome buttons: ✓ Correct / ✗ Incorrect (submits to API)
- AdversarialTestBadge: "Stress Test: PASSED/FAILED" with color

2. frontend/src/app/evolution/page.tsx + components/evolution/:
- EvolutionMetrics: week-over-week improvement score (+12.3%)
- WeightChanges: before/after signal weights as grouped bar chart
- NewRulesCard: list of proposed new detection rules
- BacktestResults: "Re-ran 7 decisions with new weights: 5/7 correct (+1)"
- ApproveButton: "Apply Weight Update" → POST /api/v1/evolution/approve/{id}
- SelfImprovementScore: large number display with trend arrow
```

---

## 🧪 PHASE 6 — Tests + README (Day 3, ~1 hour)

### Prompt 6.1 — Tests
```
Generate test files for all 6 agents and the pipeline:

For each agent test file (tests/test_{agent_name}.py):
- Import and use pytest-asyncio
- Mock LLM calls with pytest-mock (never hit real API)
- Test schema validation: agent output matches Pydantic schema
- Test demo mode: run_demo() returns correct data type
- Test error handling: what happens when LLM fails
- Test streaming: events are yielded in correct order (START, TOKEN×N, COMPLETE)

For tests/test_pipeline_e2e.py:
- Full pipeline on synthetic data
- Assert: 3+ blind spots detected
- Assert: 3+ attacks generated
- Assert: 1+ traceback result
- Assert: decision output is valid
- Assert: all events are valid AgentEvents
- Use hypothesis for property-based schema testing

For tests/test_memory.py:
- VectorMemory: store, search, deduplicate
- GraphMemory: add nodes/edges, find_paths, blast_radius, serialize/deserialize
- TimeSeriesMemory: record, query, outcome update
```

---

### Prompt 6.2 — README
```
Generate README.md for NEXUS AI.

Include:
- Project title + tagline ("AI adversary embedded in your financial stack")
- One-paragraph description of what it does
- Architecture diagram (ASCII art showing 6 agents)
- Quick Start: 3 commands to go from zero to demo
- Demo walkthrough: what to expect in each of the 6 minutes
- Hidden patterns table (what Nexus detects in the synthetic data)
- Environment variables reference (link to .env.example)
- API reference summary (key endpoints with examples)
- Tech stack table (backend + frontend)
- Project structure tree
- Contributing section
- License: MIT

Make it look polished, like a serious fintech project.
Use badges: Python version, FastAPI, Next.js, Claude-powered.
```

---

## 🎯 PHASE 7 — Polish & Integration (Day 3, ~1 hour)

### Prompt 7.1 — Demo Run Verification
```
The entire NEXUS AI codebase is now implemented. 

Do a complete review pass:
1. Check that all imports are consistent (no missing imports, no circular imports)
2. Verify all Pydantic schemas are correctly used (no v1 syntax remaining)
3. Check that demo mode works without any API keys
4. Verify the WebSocket protocol: client messages match server handlers
5. Check the React component props match the TypeScript types
6. Verify the Zustand store actions cover all WSEvent types

List any issues found and fix them.
Then generate a final demo_checklist.md:
- [ ] Start backend: uvicorn backend.main:app --reload
- [ ] Start frontend: cd frontend && npm run dev
- [ ] Open http://localhost:3000
- [ ] Click "Run Pipeline (Demo)"
- [ ] Watch all 6 agents stream output
- [ ] Verify 3+ blind spots on dashboard
- [ ] Open Traceback page — check graph renders
- [ ] Open Decisions page — verify trade + loan decisions
- [ ] Open Evolution page — verify +12.3% improvement shown
- [ ] Submit an outcome (Correct/Incorrect) on a decision
- [ ] Trigger manual evolution cycle
```

---

### Prompt 7.2 — Connector Agent (Bonus)
```
Generate backend/connectors/ — all four data source connectors.

BaseConnector (base.py):
- Abstract class with: source_name, is_demo, connect(), fetch_*() methods
- Connection status tracking with timestamps
- Demo mode: loads from data/demo/{source}_data.json

CRMConnector (crm_connector.py):
- Demo: loads crm_data.json
- Live: Salesforce REST API (requires SALESFORCE_* env vars)
- fetch_deals() → List[CRMDeal]
- Normalize to schema

BankConnector (bank_connector.py):
- Demo: loads bank_data.json
- Live: Plaid API (requires PLAID_* env vars)
- fetch_transactions(days=30) → List[BankTransaction]
- fetch_cash_flow_forecast() → dict

TradingConnector (trading_connector.py):
- Demo: loads trading_data.json
- Live: Alpaca Markets API (paper trading safe)
- fetch_positions() → List[TradingPosition]
- fetch_order_book(ticker) → OrderBook

NewsConnector (news_connector.py):
- Demo: loads news_data.json
- Live: NewsAPI (requires NEWS_API_KEY)
- fetch_news(entities=None, days=7) → List[NewsItem]
```

---

## 📋 QUICK REFERENCE

### Build Order (Critical Path)
```
schemas → config → llm_client → audit_log+errors → synthetic_data
  → memory (vector → graph → timeseries → layer)
  → agents (base → silent_finder → adversarial → traceback → decision → evolution → orchestrator)
  → api (main → routers)
  → frontend (types → store → hooks → design → components → pages)
  → tests → README
```

### Key Files to Generate First
1. `backend/schemas/models.py` — everything imports from here
2. `backend/config.py` — everything uses config
3. `backend/utils/llm_client.py` — all agents use this
4. `backend/agents/base.py` — all agents inherit from this

### Demo Mode Flag
Set in `.env`: `NEXUS_DEMO_MODE=true`
This makes EVERYTHING work without API keys.

### Running Without API Keys
```bash
cp .env.example .env   # NEXUS_DEMO_MODE=true by default
./scripts/start_nexus.sh
```

### If Cursor Gets Confused
Ask: "Read .cursor/rules/nexus.mdc and re-read docs/SE.md, then continue with [task]"
