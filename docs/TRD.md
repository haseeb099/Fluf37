# NEXUS AI — Technical Requirements Document
**Version:** 2.0 | **Status:** FINAL | **Date:** June 2026

---

## 1. System Architecture

### 1.1 High-Level Architecture
```
┌────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                             │
│  Next.js 14 App Router | WebSocket Client | REST Client         │
└───────────────────────────────┬────────────────────────────────┘
                                │ HTTPS / WSS
┌───────────────────────────────▼────────────────────────────────┐
│                       API GATEWAY LAYER                          │
│  FastAPI 0.110+ | WebSocket Manager | JWT Auth | Rate Limiter   │
└──────┬──────────────┬──────────────┬──────────────┬────────────┘
       │              │              │              │
┌──────▼──────┐ ┌─────▼──────┐ ┌────▼─────┐ ┌─────▼──────┐
│  ORCHESTR.  │ │ CONNECTOR  │ │  MEMORY  │ │  EVOLUTION │
│   AGENT     │ │   AGENT    │ │  LAYER   │ │   AGENT    │
│  (LLM Core) │ │ (CRM/Bank/ │ │ Vector + │ │ (Reward +  │
│             │ │  Trading)  │ │ Graph +  │ │  Retrain)  │
└──────┬──────┘ └────────────┘ │    TS    │ └────────────┘
       │                       └──────────┘
 ┌─────┼──────────────────────────────────┐
 │     │                                  │
┌▼─────▼──────┐ ┌──────────────┐ ┌────────▼───────┐
│   SILENT    │ │ ADVERSARIAL  │ │   TRACEBACK    │
│   FINDER    │ │  RED TEAM    │ │     AGENT      │
│   AGENT     │ │    AGENT     │ │  (RAG + Graph) │
└─────────────┘ └──────────────┘ └────────────────┘
```

### 1.2 Data Flow
```
External Sources → Connector Agent → Normalized SourceData
    → Orchestrator dispatches to SilentFinder (async)
    → BlindSpotOutput → Orchestrator dispatches to AdversarialRedTeam
    → AttackOutput → Orchestrator dispatches to TracebackAgent (async)
    → TracebackOutput → DecisionAgent (aggregates all signals)
    → DecisionOutput → EvolutionAgent (stores for weekly cycle)
    → All steps: stream tokens via WebSocket → Dashboard renders live
    → All outputs: stored in Memory Layer
```

---

## 2. Technology Stack

### 2.1 Backend
| Component | Technology | Version | Rationale |
|-----------|-----------|---------|-----------|
| Runtime | Python | 3.11+ | Async, type hints, match statements |
| API Framework | FastAPI | 0.110+ | Async, OpenAPI auto-docs, WebSocket |
| Agent Framework | LangChain | 0.2+ | Tool calling, ReAct, RAG |
| LLM Primary | Anthropic Claude | claude-3-5-sonnet-20241022 | Best reasoning + tool use |
| LLM Fallback | OpenAI GPT-4o | latest | Multi-model redundancy |
| Vector DB | ChromaDB | 0.5+ | In-process for demo, no server needed |
| Graph DB | NetworkX | 3.x | Pure Python, serializable |
| Time Series | SQLite + pandas | built-in | Zero infrastructure |
| Task Queue | asyncio | built-in | Lightweight, demo-ready |
| Schema validation | Pydantic v2 | 2.x | Fast, strict, JSON schema export |
| Logging | structlog | latest | Structured JSON logging |
| HTTP client | httpx | latest | Async, modern |
| Settings | pydantic-settings | latest | .env loading, type-safe config |

### 2.2 Frontend
| Component | Technology | Version | Rationale |
|-----------|-----------|---------|-----------|
| Framework | Next.js | 14 (App Router) | RSC, streaming, edge runtime |
| Language | TypeScript | 5.x | Strict mode, full type safety |
| Styling | Tailwind CSS | 3.x | Utility-first, purge unused |
| UI Components | shadcn/ui | latest | Headless, accessible, customizable |
| Animation | Framer Motion | 11.x | Production-grade, GPU-accelerated |
| Charts | Recharts + D3 | latest | Composable data visualization |
| Graph Viz | React Flow | 11.x | Traceback graph with pan/zoom |
| WebSocket | Custom hook | - | Auto-reconnect, Zod validation |
| Global State | Zustand | 4.x | Lightweight, devtools support |
| Server State | TanStack Query | 5.x | Caching, background refresh |
| Forms | React Hook Form + Zod | 7.x + 3.x | Performance + type-safe validation |
| Schema validation | Zod | 3.x | Runtime type safety for WS messages |

### 2.3 Infrastructure (Demo)
| Component | Technology | Notes |
|-----------|-----------|-------|
| Backend server | Uvicorn | ASGI, hot reload |
| All databases | In-process | SQLite + ChromaDB in-memory |
| Environment | Python venv | `requirements.txt` |
| Frontend | Next.js dev | HMR, fast refresh |
| Single command | `start_nexus.sh` | Boots everything |

### 2.4 Infrastructure (Production)
| Component | Technology |
|-----------|-----------|
| Container | Docker + Docker Compose |
| Orchestration | Kubernetes (EKS/GKE) |
| Vector DB | Qdrant Cloud |
| Graph DB | Neo4j Aura |
| Time Series | TimescaleDB |
| Cache | Redis |
| Queue | Celery + Redis |
| Secrets | HashiCorp Vault / AWS Secrets Manager |
| Observability | OpenTelemetry → Grafana + Jaeger |
| CDN | Vercel / CloudFront |

---

## 3. Agent Technical Specifications

### 3.1 BaseAgent (Abstract)
```python
class BaseAgent(ABC):
    agent_id: ClassVar[str]
    
    def __init__(self, config: NexusConfig, memory: MemoryLayer, llm_client: LLMClient):
        self.config = config
        self.memory = memory
        self.llm = llm_client
        self.logger = structlog.get_logger(agent_id=self.agent_id)
    
    @abstractmethod
    async def run(self, payload: BaseModel) -> AsyncIterator[AgentEvent]: ...
    
    async def run_demo(self) -> AsyncIterator[AgentEvent]:
        """Returns pre-seeded demo output for reliable demos"""
        ...
    
    def _emit(self, type: str, data: Any) -> AgentEvent:
        return AgentEvent(type=type, agent_id=self.agent_id, data=data, timestamp=datetime.utcnow())
```

### 3.2 Orchestrator
```python
# Pattern: Router + Context Manager + Priority Queue
# Maintains OrchestratorContext: shared dict for inter-agent data
# Dispatches agents in dependency order
# Streams all agent events to WebSocket manager

Pipeline order:
  1. connector (parallel)
  2. silent_finder (depends on: connector)
  3. adversarial (depends on: silent_finder) — parallel per blind spot
  4. traceback (depends on: adversarial)
  5. decision (depends on: traceback + all signals)
  6. evolution (background, depends on: decision + feedback)

Context window management:
  Max tokens per dispatch: 4096
  Rolling context: last 10 agent outputs
  Priority queue: Critical > High > Medium > Low
```

### 3.3 Silent Forcing Finder
```python
# Pattern: Statistical inference + LLM chain-of-thought
# Step 1: Compute metric coverage matrix from all sources
# Step 2: Mutual Information scoring for cross-source relationships
# Step 3: Gap analysis — which high-MI variables are unmeasured?
# Step 4: LLM hypothesizes what the missing variables represent
# Step 5: Statistical significance testing (p-values)
# Step 6: Severity scoring with dollar loss estimation
# Step 7: Counterfactual reasoning — "If tracked, would have caught X"

Severity thresholds:
  Critical: p < 0.001 AND estimated_loss > 100_000
  High:     p < 0.01  AND estimated_loss > 10_000
  Medium:   p < 0.05  AND estimated_loss > 0
  Low:      p < 0.1   (informational)
```

### 3.4 Adversarial Red Team
```python
# Pattern: ReAct (Reason → Act → Observe) loop
# Max iterations: 5 per attack path
# Attack library: versioned JSON, grows each evolution cycle

ReAct loop per blind spot:
  Thought: "Current detection rule is X. What logical gap exists?"
  Action: Generate exploit scenario targeting the gap
  Observation: Score success probability (0.0–1.0)
  Thought: "Refine attack to increase success probability"
  ... repeat up to 5 times, keep highest-scoring path

Attack taxonomy:
  - FRAUD: payment manipulation, circular flows
  - SPOOFING: order book, price feeds
  - CONCENTRATION: customer/shareholder overlap
  - TIMING: cash flow mismatch exploitation
  - INFORMATION: asymmetric data access

For each attack: auto-generate proposed_defense and rule_update
```

### 3.5 Traceback Agent
```python
# Pattern: RAG over ChromaDB + NetworkX graph traversal
# Embedding: text-embedding-3-small (or all-MiniLM-L6-v2 for offline)

Pipeline:
  1. Embed current attack/blind_spot description → vector
  2. ChromaDB similarity search (top-5, cosine similarity)
  3. Filter by metadata: source_ids, severity, date_range
  4. NetworkX traversal: BFS from matched nodes to "loss_event" nodes
  5. Score each path by: edge_probabilities × node_confidence
  6. LLM synthesizes narrative from top-3 paths
  7. "Blast radius" estimation: count connected assets

Graph schema:
  Nodes: { id, type: "failure|blind_spot|attack|loss_event", data, timestamp }
  Edges: { source, target, probability, relationship_type, timestamp }
```

### 3.6 Decision Agent
```python
# Pattern: Mixture of Experts with adaptive weights
# Four expert signals, each returns (recommendation, confidence, reasoning)

Expert signals:
  technical:   TechnicalAnalyzer(trading_data)   # RSI, MACD, imbalance
  fundamental: FundamentalAnalyzer(crm_data)      # deal health, concentration
  news:        NewsAnalyzer(news_data)             # sentiment, named entities
  forcing:     ForcingSignal(blind_spots, attacks) # Nexus's unique edge

Aggregation:
  weighted_score = Σ(weight_i × confidence_i × recommendation_i)
  
Adversarial check:
  For every recommendation: run AdversarialRedTeam.stress_test()
  If stress_test.success_probability > 0.7: add warning flag

Sensitivity analysis:
  For each signal: compute ∂(decision)/∂(signal_weight)
  Report which signal most influenced the output

Output includes: signal_breakdown, adversarial_passed, counterfactual
```

### 3.7 Evolution Agent
```python
# Pattern: Reward model + Gradient descent proxy + Human-in-the-loop
# Runs weekly (or manual trigger)

Weekly cycle:
  1. Load all decisions from past evolution_cycle_days (default: 7)
  2. Load user-submitted outcomes (POST /api/v1/decisions/{id}/outcome)
  3. Compute reward: correct=+1, incorrect=-1, no_feedback=0
  4. Update signal weights: w_new = w_old + lr * Σ(reward * signal_contribution)
  5. Detect overfitting: if false_positive_rate > 0.3, reduce weight update
  6. Propose new attack library entries from observed near-misses
  7. Propose new detection rules from successful traceback paths
  8. Generate human-readable evolution report
  9. AWAIT human approval before applying any changes

Safeguards:
  Max weight change per cycle: ±0.15
  Minimum feedback required: 5 outcomes
  Human approval: required (never auto-apply)
```

---

## 4. Memory Layer Architecture

### 4.1 Vector Memory (ChromaDB)
```python
Collection: "nexus_failures"
Embedding: text-embedding-3-small (1536-dim) or all-MiniLM-L6-v2 (384-dim, offline)
Distance: cosine

Document structure:
  text: "Failure description + context narrative"
  metadata: {
    agent_id: str,
    severity: "critical|high|medium|low",
    source_ids: List[str],
    timestamp: ISO8601,
    dollar_loss: Optional[float],
    attack_type: Optional[str],
    resolved: bool
  }

Operations:
  store(text, metadata) → doc_id
  search(query, n=5, filter=metadata_dict) → List[MemoryResult]
  delete(doc_id)
  get_size() → int
```

### 4.2 Graph Memory (NetworkX)
```python
Graph: directed, weighted, multigraph
Serialization: JSON (data/graph.json) after every mutation

Node types:
  "failure"    — historical failure record
  "blind_spot" — detected missing metric
  "attack"     — adversarial attack scenario
  "loss_event" — confirmed financial loss

Edge types:
  "leads_to"      — A caused B (probability-weighted)
  "similar_to"    — semantic similarity > 0.8
  "exploits"      — attack targets blind_spot
  "prevented_by"  — defense prevented attack

Operations:
  add_node(id, type, data)
  add_edge(source, target, type, probability)
  find_paths(source, target, max_hops=7) → List[Path]
  get_blast_radius(node_id) → Set[str]  # BFS neighbor set
  serialize() / deserialize()
```

### 4.3 Time Series (SQLite)
```sql
-- Agent performance over time
CREATE TABLE agent_metrics (
  id TEXT PRIMARY KEY,
  agent_id TEXT NOT NULL,
  timestamp DATETIME NOT NULL,
  tokens_used INTEGER,
  latency_ms INTEGER,
  success BOOLEAN,
  model TEXT
);

-- All decisions with outcomes
CREATE TABLE decisions (
  id TEXT PRIMARY KEY,
  type TEXT NOT NULL,           -- "trade|loan|risk_flag"
  recommendation TEXT NOT NULL,
  confidence REAL,
  signal_breakdown JSON,
  outcome TEXT,                 -- "correct|incorrect|pending"
  outcome_submitted_at DATETIME,
  created_at DATETIME NOT NULL
);

-- Evolution cycles
CREATE TABLE evolution_cycles (
  id TEXT PRIMARY KEY,
  period_start DATETIME,
  period_end DATETIME,
  weight_changes JSON,
  new_rules JSON,
  self_improvement_score REAL,
  approved_by TEXT,
  applied_at DATETIME,
  created_at DATETIME NOT NULL
);
```

---

## 5. Frontend Architecture

### 5.1 Page Structure
```
app/
├── page.tsx                 # Dashboard — agent grid + live pipeline
├── layout.tsx               # Root layout: sidebar + WebSocket provider
├── agents/
│   └── page.tsx             # Agent console: streaming reasoning output
├── traceback/
│   └── page.tsx             # Traceback graph: React Flow visualization
├── decisions/
│   └── page.tsx             # Decisions: trade + loan outputs
├── evolution/
│   └── page.tsx             # Evolution: self-improvement metrics
└── api/                     # API routes (Next.js, for BFF patterns)
```

### 5.2 Component Architecture
```
components/
├── layout/
│   ├── Sidebar.tsx           # Navigation + agent status indicators
│   ├── Header.tsx            # Top bar + connection status + run button
│   ├── StatusBar.tsx         # Bottom bar: last update, memory size
│   └── CommandPalette.tsx    # ⌘K power user shortcuts
├── dashboard/
│   ├── AgentGrid.tsx         # 6 cards, one per agent, live status
│   ├── PipelineFlow.tsx      # Animated pipeline: connector→...→evolution
│   ├── BlindSpotCard.tsx     # Collapsible blind spot with chain-of-thought
│   ├── AttackCard.tsx        # Attack scenario with step animator
│   └── MetricsPanel.tsx      # Key numbers: blind spots, attacks, memory size
├── agents/
│   ├── AgentConsole.tsx      # Real-time streaming terminal
│   ├── ReasoningChain.tsx    # Expandable chain-of-thought viewer
│   └── AgentStatusBadge.tsx  # Animated status: idle/running/complete/error
├── traceback/
│   ├── TraceGraph.tsx        # React Flow with custom node types
│   ├── GraphControls.tsx     # Zoom, filter, layout options
│   └── FailureTimeline.tsx   # Chronological failure list
├── decisions/
│   ├── TradeDecision.tsx     # Trade signal with signal breakdown
│   ├── LoanDecision.tsx      # Loan recommendation with risk factors
│   ├── ConfidenceMeter.tsx   # Animated arc gauge
│   └── SensitivityChart.tsx  # Bar chart: signal contributions
└── shared/
    ├── StreamingText.tsx     # Typewriter with cursor blink
    ├── SeverityBadge.tsx     # Color-coded severity pill
    ├── ConfidenceBar.tsx     # Animated progress bar
    └── JsonViewer.tsx        # Collapsible JSON tree for raw output
```

### 5.3 State Management
```typescript
// nexusStore.ts — Zustand
interface NexusStore {
  // Pipeline state
  pipelineState: PipelineState; // IDLE|CONNECTING|...|COMPLETE
  agentStates: Record<AgentId, AgentState>;
  
  // Agent outputs (accumulated)
  agentTokens: Record<AgentId, string>;    // streaming buffer
  agentOutputs: Record<AgentId, unknown>;  // finalized outputs
  
  // Domain data
  blindSpots: BlindSpot[];
  attacks: Attack[];
  tracebacks: TracebackResult[];
  decisions: DecisionOutput[];
  evolutionReport: EvolutionReport | null;
  
  // Memory
  memorySize: number;
  
  // Actions
  startPipeline: () => void;
  handleWSEvent: (event: WSEvent) => void;
  resetPipeline: () => void;
  submitOutcome: (decisionId: string, outcome: 'correct' | 'incorrect') => void;
}
```

### 5.4 WebSocket Hook
```typescript
// hooks/useNexusWebSocket.ts
export function useNexusWebSocket(url: string) {
  // Auto-reconnect with exponential backoff (max 30s)
  // Zod validation on every incoming message
  // Heartbeat ping every 30s
  // Buffers messages during reconnect
  // Returns: { isConnected, send, lastEvent }
}
```

### 5.5 Design System
```css
/* globals.css — Obsidian Intelligence Theme */
:root {
  /* Background spectrum */
  --bg-void: #020408;
  --bg-surface: #070d14;
  --bg-elevated: #0d1825;
  --bg-overlay: #152333;

  /* Brand — Electric Cyan */
  --accent-primary: #00d4ff;
  --accent-secondary: #0099cc;
  --accent-glow: rgba(0, 212, 255, 0.15);

  /* Agent identity colors */
  --agent-connector: #00ff88;
  --agent-finder: #ff9900;
  --agent-adversarial: #ff3366;
  --agent-traceback: #9966ff;
  --agent-decision: #00d4ff;
  --agent-evolution: #ffff00;

  /* Severity */
  --severity-critical: #ff1744;
  --severity-high: #ff6d00;
  --severity-medium: #ffd600;
  --severity-low: #00e676;

  /* Typography */
  --font-display: 'Space Grotesk', sans-serif;
  --font-mono: 'JetBrains Mono', monospace;
  --font-body: 'DM Sans', sans-serif;
  
  /* Spacing scale */
  --space-1: 4px; --space-2: 8px; --space-3: 12px;
  --space-4: 16px; --space-6: 24px; --space-8: 32px;
}
```

---

## 6. API Specification

### 6.1 REST Endpoints
```
# Pipeline
POST   /api/v1/nexus/run                    # Run full pipeline
POST   /api/v1/nexus/run/demo               # Run with synthetic data
GET    /api/v1/nexus/status                 # Pipeline state

# Agents
POST   /api/v1/agents/{id}/run              # Run single agent
GET    /api/v1/agents/status                # All agent statuses

# Data Sources
POST   /api/v1/connect/{source}             # Connect: crm|bank|trading|news
GET    /api/v1/sources/status               # All connection statuses

# Memory
GET    /api/v1/memory/search?q=...          # Semantic search
GET    /api/v1/memory/graph                 # Full graph (nodes + edges)
GET    /api/v1/memory/stats                 # Size, oldest entry, etc.

# Decisions
GET    /api/v1/decisions                    # List (paginated)
GET    /api/v1/decisions/{id}               # Single decision
POST   /api/v1/decisions/{id}/outcome       # Submit outcome feedback

# Evolution
GET    /api/v1/evolution/report             # Latest evolution report
POST   /api/v1/evolution/run                # Trigger manual evolution cycle
POST   /api/v1/evolution/approve/{cycle_id} # Approve + apply update

# Webhook ingestion
POST   /ingest/{source}                     # CRM/bank/trading events
```

### 6.2 WebSocket Protocol
```
WS /ws/nexus/stream

# Client → Server
{ "type": "RUN_PIPELINE", "mode": "demo|live" }
{ "type": "RUN_AGENT", "agent_id": "...", "payload": {...} }
{ "type": "PING" }
{ "type": "RESET" }

# Server → Client
{ "type": "AGENT_START",    "agent_id": "...", "timestamp": "..." }
{ "type": "AGENT_TOKEN",    "agent_id": "...", "data": "<token>", "timestamp": "..." }
{ "type": "AGENT_COMPLETE", "agent_id": "...", "data": {...}, "timestamp": "..." }
{ "type": "AGENT_ERROR",    "agent_id": "...", "data": "<error>", "timestamp": "..." }
{ "type": "PIPELINE_STATE", "state": "ANALYZING|ATTACKING|...", "timestamp": "..." }
{ "type": "PONG", "timestamp": "..." }
```

---

## 7. Synthetic Data Specification

### Hidden Patterns (must be detected by demo)
| Pattern | Location | What Nexus Finds |
|---------|----------|-----------------|
| Circular loop (3-step) | bank_data.json | Acme → Supplier X → Shell Co → Acme |
| Circular loop (4-step) | bank_data.json | More complex variant |
| Cash flow timing mismatch | CRM + bank | 90-day terms vs 30-day forecast |
| Customer-shareholder overlap | crm_data.json | CFO = 40% equity holder |
| Order book imbalance | trading_data.json | -0.32 imbalance, RSI divergence |
| Shell company flag | bank_data.json | Tx to company registered 3 days ago |

---

## 8. Security Requirements

- All API keys in environment variables only
- LLM prompts sanitized (strip injection patterns)
- All agent outputs validated against Pydantic schemas before storage
- No PII stored in vector embeddings (strip names, account numbers)
- Audit log: append-only, sha256 hash chain, tamper detection on read
- CORS: locked to known origins in production
- Rate limiting: 100 req/min per API key (in-memory for demo, Redis in prod)

---

## 9. Performance Targets

| Metric | Target | Method |
|--------|--------|--------|
| First LLM token | < 500ms | Streaming response |
| Full pipeline | < 30s | Async parallel agents |
| Vector search | < 100ms | In-memory ChromaDB |
| Graph query | < 50ms | NetworkX in-memory |
| Dashboard load | < 2s | Static + streaming |
| WS reconnect | < 1s | Exponential backoff |
| Demo cold start | < 60s | Pre-seeded data |

---

## 10. Deployment

### Demo (Single Command)
```bash
./scripts/start_nexus.sh
# 1. pip install -r requirements.txt
# 2. python scripts/generate_demo_data.py --seed 42
# 3. uvicorn backend.main:app --reload --port 8000 &
# 4. cd frontend && npm install && npm run dev &
# echo "Nexus running at http://localhost:3000"
```

### Production (Docker)
```bash
docker-compose up --build
# Services: api, worker, frontend, chromadb, postgres, redis
```
