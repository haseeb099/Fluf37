"""Pydantic v2 schemas for Nexus AI."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional, Union
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

# --- Enums as Literals ---
SourceType = Literal["crm", "erp", "bank", "trading", "news", "custom", "webhook"]
ConnectionState = Literal["disconnected", "connecting", "connected", "degraded", "error"]
Severity = Literal["critical", "high", "medium", "low"]
AgentId = Literal["connector", "silent_finder", "adversarial", "traceback", "decision", "evolution"]
PipelineState = Literal[
    "IDLE", "CONNECTING", "CONNECTED", "ANALYZING", "ATTACKING",
    "TRACING", "DECIDING", "EVOLVING", "COMPLETE", "ERROR",
]
AgentEventType = Literal[
    "AGENT_START", "AGENT_TOKEN", "AGENT_COMPLETE", "AGENT_ERROR",
    "PIPELINE_STATE", "SOURCE_SYNC_START", "SOURCE_SYNC_COMPLETE", "PONG",
]
AttackType = Literal["fraud", "spoofing", "concentration", "timing", "information"]
DecisionType = Literal["trade", "loan", "risk_flag"]
OutcomeType = Literal["correct", "incorrect", "pending"]


# --- Source Data ---
class EquityHolder(BaseModel):
    name: str
    equity_pct: float


class CRMDeal(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    company: str
    contact_name: str = ""
    contact_role: str = ""
    deal_value: float = 0.0
    stage: str = ""
    payment_terms_days: int = 30
    equity_holders: List[EquityHolder] = Field(default_factory=list)
    is_at_risk: bool = False
    risk_reason: Optional[str] = None


class BankTransaction(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    amount: float
    from_account: str = ""
    to_entity: str = ""
    to_account: str = ""
    timestamp: str = ""
    category: str = ""
    description: str = ""
    is_flagged: bool = False


class TradingPosition(BaseModel):
    model_config = ConfigDict(extra="ignore")
    ticker: str
    qty: float = 0.0
    entry_price: float = 0.0
    current_price: float = 0.0
    order_book_imbalance: float = 0.0
    rsi: float = 50.0
    pre_earnings: bool = False


class NewsItem(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    headline: str
    body: str = ""
    sentiment: float = 0.0
    entities: List[str] = Field(default_factory=list)
    timestamp: str = ""


class ERPVendor(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    name: str
    total_paid_ytd: float = 0.0
    pct_of_total_spend: float = 0.0
    payment_terms_days: int = 30
    crm_entity_id: Optional[str] = None
    linked_bank_entity: Optional[str] = None


class GLSnapshot(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    account: str
    balance: float
    projected_30d_outflow: float = 0.0
    projected_30d_inflow: float = 0.0


class VendorPayment(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    vendor_id: str
    amount: float
    timestamp: str = ""
    crm_deal_id: Optional[str] = None


class ERPRecord(BaseModel):
    vendors: List[ERPVendor] = Field(default_factory=list)
    gl_snapshots: List[GLSnapshot] = Field(default_factory=list)
    vendor_payments: List[VendorPayment] = Field(default_factory=list)


class SourceData(BaseModel):
    crm: List[CRMDeal] = Field(default_factory=list)
    bank: List[BankTransaction] = Field(default_factory=list)
    trading: List[TradingPosition] = Field(default_factory=list)
    news: List[NewsItem] = Field(default_factory=list)
    erp: ERPRecord = Field(default_factory=ERPRecord)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source_ids: List[str] = Field(default_factory=list)


# --- Connector / Integration ---
class ConnectionStatus(BaseModel):
    source_type: SourceType
    state: ConnectionState = "disconnected"
    last_sync: Optional[datetime] = None
    freshness_seconds: Optional[float] = None
    message: Optional[str] = None
    warning: Optional[str] = None


class ConnectorConfig(BaseModel):
    source_type: SourceType
    enabled: bool = True
    demo: bool = True
    credentials_ref: Optional[str] = None


class SyncResult(BaseModel):
    source_type: SourceType
    success: bool
    records_fetched: int = 0
    latency_ms: int = 0
    error: Optional[str] = None


class ConnectorOutput(BaseModel):
    source_data: SourceData
    connections: List[ConnectionStatus] = Field(default_factory=list)
    sync_results: List[SyncResult] = Field(default_factory=list)


class IngestEvent(BaseModel):
    source_type: SourceType
    payload: Dict[str, Any]
    tenant_id: str = "default"
    received_at: datetime = Field(default_factory=datetime.utcnow)


# --- Agent outputs ---
class BlindSpot(BaseModel):
    id: str
    title: str
    description: str
    severity: Severity
    estimated_loss: Optional[float] = None
    connected_sources: List[str] = Field(default_factory=list)
    chain_of_thought: List[str] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1)
    counterfactual: Optional[str] = None


class BlindSpotOutput(BaseModel):
    blind_spots: List[BlindSpot] = Field(default_factory=list)


class Attack(BaseModel):
    id: str
    name: str
    target_blind_spot_id: str
    attack_type: AttackType
    success_probability: float = Field(ge=0, le=1)
    steps: List[str] = Field(default_factory=list)
    current_rule_exploited: str = ""
    proposed_defense: str = ""
    library_version: str = "v1"


class AttackOutput(BaseModel):
    attacks: List[Attack] = Field(default_factory=list)


class FailureRecord(BaseModel):
    id: str
    description: str
    source_ids: List[str] = Field(default_factory=list)
    dollar_loss: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    resolved: bool = False
    severity: Severity = "medium"


class TimelineEvent(BaseModel):
    date: str
    event: str
    severity: Severity = "medium"


class TracebackResult(BaseModel):
    similar_failures: List[FailureRecord] = Field(default_factory=list)
    graph_path: List[str] = Field(default_factory=list)
    connection_probability: float = 0.0
    rule_update_recommendations: List[str] = Field(default_factory=list)
    timeline: List[TimelineEvent] = Field(default_factory=list)
    blast_radius: List[str] = Field(default_factory=list)
    narrative: str = ""


class TracebackOutput(BaseModel):
    tracebacks: List[TracebackResult] = Field(default_factory=list)


class SignalWeights(BaseModel):
    technical: float = 0.30
    fundamental: float = 0.25
    news: float = 0.20
    forcing: float = 0.25

    @model_validator(mode="after")
    def weights_sum(self) -> "SignalWeights":
        total = self.technical + self.fundamental + self.news + self.forcing
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"Weights must sum to 1.0, got {total}")
        return self


class DecisionOutput(BaseModel):
    id: str = Field(default_factory=lambda: f"dec_{uuid4().hex[:8]}")
    decision_type: DecisionType
    recommendation: str
    confidence: float = Field(ge=0, le=1)
    adversarial_stress_passed: bool = True
    signal_breakdown: Dict[str, float] = Field(default_factory=dict)
    sensitivity: Dict[str, float] = Field(default_factory=dict)
    reasoning: str = ""
    chain_of_thought: List[str] = Field(default_factory=list)
    traceback_chain: List[str] = Field(default_factory=list)
    counterfactual: Optional[str] = None
    outcome: OutcomeType = "pending"


class EvolutionReport(BaseModel):
    period_days: int = 7
    attacks_generated: int = 0
    blind_spots_found: int = 0
    decisions_made: int = 0
    decisions_with_feedback: int = 0
    correct_predictions: int = 0
    false_positive_rate: float = 0.0
    weight_changes: Dict[str, float] = Field(default_factory=dict)
    new_rules: List[str] = Field(default_factory=list)
    self_improvement_score: float = 0.123
    backtest_score: float = 0.0
    regime_shift_detected: bool = False
    approval_required: bool = True


class EvolutionCycle(BaseModel):
    id: str = Field(default_factory=lambda: f"evo_{uuid4().hex[:8]}")
    weight_changes: Dict[str, float] = Field(default_factory=dict)
    new_rules: List[str] = Field(default_factory=list)
    approved: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)


# --- Agent events ---
class AgentEvent(BaseModel):
    type: AgentEventType
    agent_id: str
    data: Union[str, dict, list] = ""
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class NexusReport(BaseModel):
    connector: Optional[ConnectorOutput] = None
    silent_finder: Optional[BlindSpotOutput] = None
    adversarial: Optional[AttackOutput] = None
    traceback: Optional[TracebackOutput] = None
    decisions: List[DecisionOutput] = Field(default_factory=list)
    evolution: Optional[EvolutionReport] = None
    pipeline_state: PipelineState = "COMPLETE"


# --- Memory ---
class MemoryMetadata(BaseModel):
    agent_id: str = ""
    severity: Severity = "medium"
    source_ids: List[str] = Field(default_factory=list)
    source_types: List[str] = Field(default_factory=list)
    timestamp: str = ""
    dollar_loss: Optional[float] = None
    attack_type: Optional[str] = None
    resolved: bool = False


class MemoryResult(BaseModel):
    id: str
    text: str
    score: float
    metadata: MemoryMetadata


class MemoryStats(BaseModel):
    vector_count: int = 0
    graph_nodes: int = 0
    graph_edges: int = 0
    decisions_count: int = 0


# --- Audit ---
class AuditEntry(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    agent_id: str = "system"
    action: str
    payload_preview: str = ""
    tokens: int = 0
    latency_ms: int = 0
    model: str = ""
    tenant_id: str = "default"


class AuditVerification(BaseModel):
    valid: bool
    entries_checked: int = 0
    first_invalid_index: Optional[int] = None


# --- API requests ---
class RunPipelineRequest(BaseModel):
    mode: Literal["demo", "live"] = "demo"
    tenant_id: str = "default"


class OutcomeRequest(BaseModel):
    outcome: Literal["correct", "incorrect"]


class WSClientMessage(BaseModel):
    type: Literal["RUN_PIPELINE", "RUN_AGENT", "PING", "RESET"]
    mode: Optional[Literal["demo", "live"]] = "demo"
    agent_id: Optional[str] = None
