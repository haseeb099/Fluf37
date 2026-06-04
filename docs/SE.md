# NEXUS AI — System Engineering Document
**Version:** 2.0 | **Status:** FINAL | **Date:** June 2026

---

## 1. Engineering Principles

1. **Agent Isolation** — Each agent runs independently. Failure in one doesn't cascade.
2. **Stream First** — All LLM outputs stream to client via WebSocket. No waiting for full responses.
3. **Memory Persistence** — Every agent output stored. System improves passively over time.
4. **Zero External Dependencies (Demo)** — Runs fully offline with synthetic data. No API keys for demo.
5. **Explainability by Design** — Every output carries a `chain_of_thought` field. No black boxes.
6. **Schema-Driven** — All inter-agent communication via Pydantic v2 schemas.
7. **Human-in-the-Loop** — Evolution Agent proposes updates; humans approve before applying.
8. **Fail Gracefully** — Every agent has a rule-based fallback if LLM fails.

### 1.1 Agent Communication Protocol
```
Agents communicate via: OrchestratorContext (shared in-memory dict, typed)
Not via: Direct agent-to-agent calls (prevents coupling)

Flow:
  WebSocket.receive("RUN_PIPELINE")
    → Orchestrator.run_pipeline(source_data)
    → [PARALLEL] Orchestrator.dispatch("connector", payload)
                  → connector.run(payload) → yield AgentEvent(AGENT_TOKEN) × N
                  → yield AgentEvent(AGENT_COMPLETE, ConnectorOutput)
                  → orchestrator.context.store("connector", ConnectorOutput)
                  → memory.store(output)
    → [SEQUENTIAL] dispatch("silent_finder", context["connector"])
    → [PARALLEL]   dispatch("adversarial", context["silent_finder"])
    → [SEQUENTIAL] dispatch("traceback", context["adversarial"])
    → [SEQUENTIAL] dispatch("decision", context["all_signals"])
    → [BACKGROUND] dispatch("evolution", context["decision"])
```

---

## 2. Module Specifications

### 2.1 backend/main.py
```python
# FastAPI app entrypoint
# Routes: /api (REST), /ws (WebSocket), /ingest (webhooks), /docs (OpenAPI)
# Middleware: CORS, structured logging, API key auth
# Lifespan: 
#   on_startup: init agents, memory layer, load demo data
#   on_shutdown: flush memory, close connections
```

### 2.2 backend/config.py
```python
class NexusConfig(BaseSettings):
    # LLM
    anthropic_api_key: str = Field(default="demo", env="ANTHROPIC_API_KEY")
    openai_api_key: str = Field(default="demo", env="OPENAI_API_KEY")
    primary_model: str = "claude-3-5-sonnet-20241022"
    fallback_model: str = "gpt-4o"
    max_tokens_per_agent: int = 2048
    temperature_analysis: float = 0.3
    temperature_generation: float = 0.7
    
    # Demo
    demo_mode: bool = Field(default=True, env="NEXUS_DEMO_MODE")
    demo_seed: int = 42
    
    # Agent limits
    adversarial_max_iterations: int = 5
    traceback_max_results: int = 5
    agent_timeout_seconds: int = 30
    
    # Memory
    vector_db_path: str = "./data/chroma"
    graph_db_path: str = "./data/graph.json"
    sqlite_path: str = "./data/nexus.db"
    
    # Evolution
    evolution_cycle_days: int = 7
    min_feedback_for_update: int = 5
    max_weight_change_per_cycle: float = 0.15
    
    # Performance
    stream_chunk_size: int = 20
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
```

### 2.3 backend/agents/base.py
```python
class AgentState(str, Enum):
    WAITING = "waiting"
    DISPATCHED = "dispatched"
    RUNNING = "running"
    STREAMING = "streaming"
    COMPLETE = "complete"
    ERROR = "error"

class AgentEvent(BaseModel):
    type: Literal["AGENT_START", "AGENT_TOKEN", "AGENT_COMPLETE", "AGENT_ERROR"]
    agent_id: str
    data: Union[str, dict]
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class BaseAgent(ABC):
    agent_id: ClassVar[str]
    state: AgentState = AgentState.WAITING
    
    @abstractmethod
    async def run(self, payload: BaseModel) -> AsyncIterator[AgentEvent]: ...
    
    async def run_demo(self) -> AsyncIterator[AgentEvent]:
        """Pre-seeded demo output. Override in each agent."""
        ...
    
    async def _stream_llm(self, prompt: str, system: str) -> AsyncIterator[str]:
        """Handles streaming + fallback + timeout + audit logging"""
        ...
```

### 2.4 backend/agents/orchestrator.py
```python
class OrchestratorContext(TypedDict):
    connector: Optional[ConnectorOutput]
    silent_finder: Optional[BlindSpotOutput]
    adversarial: Optional[AttackOutput]
    traceback: Optional[TracebackOutput]
    decision: Optional[DecisionOutput]

class NexusOrchestrator:
    agents: Dict[str, BaseAgent]
    memory: MemoryLayer
    context: OrchestratorContext
    ws_manager: WebSocketManager
    
    async def run_pipeline(
        self, 
        source_data: SourceData,
        mode: Literal["demo", "live"] = "demo"
    ) -> AsyncIterator[AgentEvent]:
        # Manages full pipeline execution
        # Broadcasts all events to WebSocket manager
        # Handles partial failures gracefully
        ...
    
    async def dispatch(
        self, 
        agent_id: str, 
        payload: BaseModel
    ) -> AsyncIterator[AgentEvent]:
        # Dispatches with timeout, retry, fallback
        ...
    
    async def aggregate_results(self) -> NexusReport:
        # Combines all agent outputs into final report
        ...
```

### 2.5 backend/agents/silent_finder.py
```python
class SilentForcingFinder(BaseAgent):
    agent_id = "silent_finder"
    
    # Algorithm:
    # 1. compute_metric_coverage(data) → MetricMatrix (which sources have which metrics)
    # 2. mutual_information_score(matrix) → MIMatrix (which pairs are statistically linked)
    # 3. identify_gaps(mi_matrix) → List[Gap] (high-MI pairs with missing metrics)
    # 4. llm_hypothesize(gaps) → List[BlindSpot] [STREAMING]
    # 5. score_severity(blind_spots) → List[ScoredBlindSpot]
    # 6. counterfactual_reasoning(blind_spots) → "If tracked, would have caught..."
    
    async def run(self, payload: SourceData) -> AsyncIterator[AgentEvent]: ...
    async def compute_metric_coverage(self, data: SourceData) -> MetricMatrix: ...
    async def mutual_information_score(self, matrix: MetricMatrix) -> MIMatrix: ...
    async def identify_gaps(self, mi_matrix: MIMatrix) -> List[Gap]: ...
```

### 2.6 backend/agents/adversarial.py
```python
class AdversarialRedTeam(BaseAgent):
    agent_id = "adversarial"
    attack_library: AttackLibrary  # Loaded from data/attack_library/v{n}.json
    
    # ReAct Loop per blind spot:
    # for blind_spot in blind_spots:
    #     history = []
    #     for i in range(max_iterations=5):
    #         thought = llm_reason(blind_spot, history)   [STREAMING]
    #         action = llm_act(thought)                   [STREAMING]  
    #         observation = evaluate_attack(action)       [rule-based]
    #         history.append((thought, action, observation))
    #         if observation.success_probability > 0.7: break
    #     attacks.append(best_attack(history))
    #     attacks[-1].proposed_defense = llm_generate_defense(attacks[-1])
    
    async def run(self, payload: BlindSpotOutput) -> AsyncIterator[AgentEvent]: ...
    async def stress_test(self, recommendation: DecisionOutput) -> StressTestResult: ...
    async def update_library(self, new_attacks: List[Attack]) -> None: ...
    
    def _evaluate_attack(self, action: AttackAction) -> AttackObservation:
        """Rule-based evaluator — works without LLM"""
        ...
```

### 2.7 backend/agents/traceback.py
```python
class TracebackAgent(BaseAgent):
    agent_id = "traceback"
    collection: ChromaCollection  # "nexus_failures"
    graph: NexusGraph             # NetworkX wrapper
    
    # RAG + Graph Pipeline:
    # 1. embed(current_pattern) → vector (1536-dim)
    # 2. chroma.query(vector, n_results=5) → similar_docs
    # 3. chroma.filter(metadata: severity=critical, resolved=false)
    # 4. build_graph(similar_docs + existing_graph) → extended subgraph
    # 5. find_paths(graph, source=current_pattern, target="loss_event", max_hops=7)
    # 6. score_paths(paths) → sorted by probability
    # 7. llm_synthesize(top_3_paths, similar_docs) [STREAMING]
    # 8. estimate_blast_radius(matched_nodes)
    
    async def run(self, payload: AttackOutput) -> AsyncIterator[AgentEvent]: ...
    async def store_failure(self, failure: FailureRecord) -> None: ...
    async def get_blast_radius(self, node_id: str) -> BlastRadius: ...
```

### 2.8 backend/agents/decision.py
```python
class DecisionAgent(BaseAgent):
    agent_id = "decision"
    weights: SignalWeights  # From Evolution Agent, persisted in SQLite
    
    # Mixture of Experts:
    # signals = {
    #   "technical":   TechnicalAnalyzer(trading_data).analyze() → (rec, conf, reasoning)
    #   "fundamental": FundamentalAnalyzer(crm_data).analyze()   → (rec, conf, reasoning)
    #   "news":        NewsAnalyzer(news_data).analyze()          → (rec, conf, reasoning)
    #   "forcing":     ForcingSignal(blind_spots, attacks).analyze() → (rec, conf, reasoning)
    # }
    # 
    # weighted_score = Σ(w_i × conf_i × rec_i) / Σ(w_i)
    # adversarial_check = red_team.stress_test(proposed_recommendation)
    # sensitivity = {sig: ∂(score)/∂(w_sig) for sig in signals}
    # output = llm_synthesize(weighted_score, adversarial_check, sensitivity) [STREAMING]
    
    async def run(self, payload: AllSignals) -> AsyncIterator[AgentEvent]: ...
    async def analyze_sensitivity(self, signals: Dict, weights: Dict) -> Dict[str, float]: ...
```

### 2.9 backend/agents/evolution.py
```python
class EvolutionAgent(BaseAgent):
    agent_id = "evolution"
    reward_model: RewardModel
    
    # Weekly cycle:
    # 1. Load decisions from SQLite (past N days)
    # 2. Load outcomes (user-submitted feedback)
    # 3. Filter: only decisions with feedback
    # 4. Compute reward per decision: correct=+1, incorrect=-1
    # 5. Update weights: w_new = clip(w_old + lr * Σ(r * contribution), 0.05, 0.60)
    # 6. Overfitting check: if false_positive_rate > 0.3 → reduce lr
    # 7. Regime detection: if last 3 decisions all wrong → flag distribution shift
    # 8. Propose attack library additions from near-misses
    # 9. Propose new detection rules from successful tracebacks
    # 10. Backtest: re-score past decisions with new weights → confirm improvement
    # 11. Generate EvolutionReport [STREAMING]
    # 12. Store as pending update → AWAIT human approval
    
    async def run_weekly_update(self) -> AsyncIterator[AgentEvent]: ...
    async def apply_approved_update(self, update: Update) -> None: ...
    async def backtest(self, new_weights: SignalWeights) -> BacktestResult: ...
    async def detect_regime_shift(self) -> Optional[RegimeShiftWarning]: ...
```

### 2.10 backend/memory/vector.py
```python
class VectorMemory:
    client: chromadb.Client
    collection_name: str = "nexus_failures"
    
    async def store(self, text: str, metadata: MemoryMetadata) -> str: ...
    async def search(self, query: str, n_results: int = 5, filter: Optional[dict] = None) -> List[MemoryResult]: ...
    async def delete(self, doc_id: str) -> None: ...
    async def get_stats(self) -> MemoryStats: ...
    async def deduplicate(self, similarity_threshold: float = 0.95) -> int: ...
```

### 2.11 backend/utils/llm_client.py
```python
class LLMClient:
    """Unified client with streaming, fallback, retry, and audit logging"""
    
    primary: AsyncAnthropic    # claude-3-5-sonnet-20241022
    fallback: AsyncOpenAI      # gpt-4o
    
    async def stream(
        self,
        messages: List[Message],
        system: str,
        temperature: float = 0.3,
        max_tokens: int = 2048,
        agent_id: str = "unknown"
    ) -> AsyncIterator[str]:
        # 1. Try primary (Anthropic) with timeout
        # 2. On LLMError/timeout: retry 3x with exponential backoff
        # 3. On 3rd failure: fall back to OpenAI
        # 4. On both failing: raise with rule-based fallback flag
        # 5. Audit log every call: model, tokens, latency, success
        ...
    
    async def complete(self, ...) -> str: ...  # Non-streaming version
```

### 2.12 backend/utils/audit_log.py
```python
class AuditLog:
    """Append-only, tamper-evident hash chain"""
    
    def write(self, entry: AuditEntry) -> str:
        # prev_hash = last entry hash (or "genesis" for first)
        # entry_json = entry.model_dump_json()
        # entry_hash = sha256(entry_json + prev_hash)
        # append to audit.jsonl
        # return entry_hash
        ...
    
    def verify(self) -> AuditVerification:
        # Re-compute all hashes, return first tampered entry if any
        ...
    
    def export(self, format: Literal["json", "pdf"]) -> bytes: ...
```

---

## 3. Pydantic Schemas (Complete)

```python
# backend/schemas/models.py

# --- Source Data ---
class CRMDeal(BaseModel):
    id: str; company: str; value: float; stage: str
    payment_terms_days: int; contacts: List[str]; equity_holders: List[str]

class BankTransaction(BaseModel):
    id: str; amount: float; from_account: str; to_account: str
    timestamp: datetime; category: str; is_circular: bool = False

class TradingPosition(BaseModel):
    ticker: str; qty: float; entry_price: float
    order_book_imbalance: float; rsi: float; pre_earnings: bool

class NewsItem(BaseModel):
    id: str; headline: str; body: str; sentiment: float  # -1 to 1
    entities: List[str]; timestamp: datetime

class SourceData(BaseModel):
    crm: List[CRMDeal]; bank: List[BankTransaction]
    trading: List[TradingPosition]; news: List[NewsItem]
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# --- Agent Outputs ---
class BlindSpot(BaseModel):
    id: str; title: str; description: str
    severity: Literal["critical", "high", "medium", "low"]
    estimated_loss: Optional[float]
    connected_sources: List[str]
    chain_of_thought: List[str]
    confidence: float
    counterfactual: Optional[str]  # "If tracked, would have caught..."

class Attack(BaseModel):
    id: str; name: str; target_blind_spot_id: str
    attack_type: Literal["fraud", "spoofing", "concentration", "timing", "information"]
    success_probability: float
    steps: List[str]
    current_rule_exploited: str
    proposed_defense: str
    library_version: str

class FailureRecord(BaseModel):
    id: str; description: str; source_ids: List[str]
    dollar_loss: Optional[float]; timestamp: datetime; resolved: bool

class TracebackResult(BaseModel):
    similar_failures: List[FailureRecord]
    graph_path: List[str]
    connection_probability: float
    rule_update_recommendations: List[str]
    timeline: List[TimelineEvent]
    blast_radius: List[str]  # affected asset IDs

class DecisionOutput(BaseModel):
    id: str = Field(default_factory=lambda: f"dec_{uuid4().hex[:8]}")
    decision_type: Literal["trade", "loan", "risk_flag"]
    recommendation: str
    confidence: float
    adversarial_stress_passed: bool
    signal_breakdown: Dict[str, float]
    sensitivity: Dict[str, float]  # ∂(decision)/∂(signal)
    reasoning: str
    chain_of_thought: List[str]
    traceback_chain: List[str]
    counterfactual: Optional[str]

class EvolutionReport(BaseModel):
    period_days: int; attacks_generated: int; blind_spots_found: int
    decisions_made: int; decisions_with_feedback: int
    correct_predictions: int; false_positive_rate: float
    user_adoption_rate: float; memory_size: int
    weight_changes: Dict[str, float]
    new_rules: List[str]; new_attacks: List[str]
    self_improvement_score: float  # week-over-week delta
    backtest_score: float
    regime_shift_detected: bool
    approval_required: bool = True

class SignalWeights(BaseModel):
    technical: float = 0.30
    fundamental: float = 0.25
    news: float = 0.20
    forcing: float = 0.25
    
    @model_validator(mode="after")
    def weights_sum_to_one(self):
        total = sum(self.model_dump().values())
        assert abs(total - 1.0) < 0.01, f"Weights must sum to 1.0, got {total}"
        return self
```

---

## 4. State Machines

### 4.1 Pipeline State
```
IDLE → CONNECTING → CONNECTED → ANALYZING → ATTACKING → TRACING → DECIDING → EVOLVING → COMPLETE
                        ↓                                                                      ↓
                     ERROR ←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←
```

### 4.2 Agent State
```
WAITING → DISPATCHED → RUNNING → STREAMING → COMPLETE
                          ↓                      ↓
                        ERROR               (stored in memory)
```

---

## 5. Error Hierarchy

```python
class NexusError(Exception):
    def __init__(self, message: str, agent_id: str = None, recoverable: bool = True): ...

class AgentError(NexusError):
    class LLMError(AgentError): ...      # API failure, rate limit → retry + fallback
    class TimeoutError(AgentError): ...  # Agent > 30s → return partial + warning
    class SchemaError(AgentError): ...   # Output doesn't match schema → log + skip

class ConnectorError(NexusError):
    class AuthError(ConnectorError): ...   # → fall back to synthetic data
    class DataError(ConnectorError): ...   # → fall back to synthetic data

class MemoryError(NexusError):
    class StorageError(MemoryError): ...  # → continue without memory, log warning

# Recovery:
# LLMError: retry 3x backoff → fallback to OpenAI → rule-based output
# TimeoutError: return partial output with warning flag
# ConnectorError: fall back to synthetic data seamlessly
# MemoryError: continue without memory, log warning
```

---

## 6. Logging & Observability

```python
# Every agent action logged as structured JSON (structlog)
{
  "timestamp": "2026-06-04T12:00:00Z",
  "agent_id": "adversarial",
  "action": "attack_generated",
  "blind_spot_id": "bs_001",
  "attack_id": "atk_007",
  "success_probability": 0.89,
  "latency_ms": 1240,
  "tokens_used": 847,
  "model": "claude-3-5-sonnet-20241022",
  "success": true,
  "audit_hash": "sha256:abc123..."
}

# Audit chain: each entry includes sha256(entry_json + prev_hash)
# Tamper detection: verify() re-computes all hashes on read
# Export: JSON lines file OR PDF compliance report
```

---

## 7. File Structure (Complete)

```
nexus-ai/
├── .cursor/
│   └── rules/
│       └── nexus.mdc              ← Cursor AI rules (CRITICAL — read first)
├── .env.example                   ← All required environment variables
├── .env                           ← Your actual keys (gitignored)
├── README.md                      ← Setup + demo guide
├── requirements.txt               ← Exact pinned dependencies
├── docker-compose.yml             ← Production deployment
├── docs/
│   ├── PRD.md                     ← Product requirements
│   ├── TRD.md                     ← Technical requirements
│   └── SE.md                      ← This file
├── backend/
│   ├── main.py                    ← FastAPI app + lifespan
│   ├── config.py                  ← NexusConfig (pydantic-settings)
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base.py                ← BaseAgent + AgentEvent + AgentState
│   │   ├── orchestrator.py        ← NexusOrchestrator + WebSocketManager
│   │   ├── silent_finder.py       ← SilentForcingFinder
│   │   ├── adversarial.py         ← AdversarialRedTeam
│   │   ├── traceback.py           ← TracebackAgent
│   │   ├── decision.py            ← DecisionAgent
│   │   └── evolution.py           ← EvolutionAgent
│   ├── connectors/
│   │   ├── __init__.py
│   │   ├── base.py                ← BaseConnector
│   │   ├── crm_connector.py       ← CRM (Salesforce/HubSpot/demo)
│   │   ├── bank_connector.py      ← Banking (Plaid/demo)
│   │   ├── trading_connector.py   ← Trading (Alpaca/demo)
│   │   └── news_connector.py      ← News (NewsAPI/demo)
│   ├── memory/
│   │   ├── __init__.py
│   │   ├── layer.py               ← MemoryLayer (facade over all 3)
│   │   ├── vector.py              ← VectorMemory (ChromaDB)
│   │   ├── graph.py               ← GraphMemory (NetworkX)
│   │   └── timeseries.py          ← TimeSeriesMemory (SQLite)
│   ├── schemas/
│   │   └── models.py              ← All Pydantic v2 schemas
│   └── utils/
│       ├── audit_log.py           ← Append-only hash chain
│       ├── llm_client.py          ← Anthropic + fallback + retry
│       └── synthetic_data.py      ← Demo data generator (seed=42)
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx           ← Dashboard
│   │   │   ├── globals.css        ← Obsidian Intelligence design tokens
│   │   │   ├── agents/page.tsx
│   │   │   ├── traceback/page.tsx
│   │   │   ├── decisions/page.tsx
│   │   │   └── evolution/page.tsx
│   │   ├── components/            ← All React components (see TRD)
│   │   ├── hooks/
│   │   │   ├── useNexusWebSocket.ts
│   │   │   └── useStreamingText.ts
│   │   ├── store/
│   │   │   └── nexusStore.ts      ← Zustand store
│   │   ├── types/
│   │   │   └── nexus.ts           ← TypeScript types (mirror Pydantic)
│   │   └── lib/
│   │       ├── utils.ts           ← cn(), formatters
│   │       └── api.ts             ← REST API client
│   ├── package.json
│   └── tsconfig.json
├── scripts/
│   ├── generate_demo_data.py      ← Generates all data/demo/*.json
│   └── start_nexus.sh             ← Single command startup
├── data/
│   ├── demo/
│   │   ├── crm_data.json
│   │   ├── bank_data.json
│   │   ├── trading_data.json
│   │   └── news_data.json
│   └── attack_library/
│       └── v1.json                ← Initial attack library
└── tests/
    ├── test_silent_finder.py
    ├── test_adversarial.py
    ├── test_traceback.py
    ├── test_decision.py
    ├── test_evolution.py
    ├── test_memory.py
    └── test_pipeline_e2e.py
```
