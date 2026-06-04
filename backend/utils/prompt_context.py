"""Compact source-data summaries for live LLM prompts."""
from __future__ import annotations

import json
from typing import Any, Iterable, List

from backend.schemas.models import (
    AttackOutput,
    BlindSpotOutput,
    ConnectorOutput,
    SourceData,
    TracebackOutput,
)

MAX_PROMPT_CHARS = 12_000

FINANCIAL_ANALYST_SYSTEM = (
    "You are Fluf37, an auditable financial intelligence analyst for mid-market CFO offices. "
    "Analyze cross-source CRM, ERP, banking, trading, and news data to surface blind spots before "
    "wires, credit lines, or large deal approvals. Cite specific dollar amounts, entity names, "
    "and payment terms from the provided context. Do not invent entities absent from the data. "
    "Write 3–6 concise sentences suitable for a streaming risk-review UI."
)

RED_TEAM_SYSTEM = (
    "You are an adversarial red-team analyst stress-testing financial control gaps. "
    "Describe realistic exploitation paths using only entities and amounts from the context. "
    "Be specific about which control rule is bypassed and estimated impact."
)

TRACEBACK_SYSTEM = (
    "You connect current attack patterns to historical failures in financial operations. "
    "Reference named incidents, loss amounts, and affected entities from the context."
)

DECISION_SYSTEM = (
    "You synthesize trade, credit, and risk-flag recommendations for a CFO review committee. "
    "State clear actions (APPROVE, REVIEW, DEFER, SELL) with confidence rationale tied to the signals."
)

EVOLUTION_SYSTEM = (
    "You propose measurable rule and weight updates based on recent decision outcomes. "
    "Keep proposals conservative; note that human approval is required before apply."
)


def _clip(text: str, limit: int = MAX_PROMPT_CHARS) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 20] + "\n… [truncated]"


def _dump(obj: Any) -> str:
    if hasattr(obj, "model_dump"):
        return json.dumps(obj.model_dump(), default=str, indent=2)
    return json.dumps(obj, default=str, indent=2)


def summarize_source_data(data: SourceData) -> str:
    crm = [
        {
            "company": d.company,
            "value": d.deal_value,
            "terms_days": d.payment_terms_days,
            "contact": d.contact_name,
            "role": d.contact_role,
            "equity_holders": [h.model_dump() for h in d.equity_holders],
            "at_risk": d.is_at_risk,
        }
        for d in data.crm
    ]
    bank = [
        {
            "amount": t.amount,
            "from": t.from_account,
            "to": t.to_entity,
            "category": t.category,
            "flagged": t.is_flagged,
        }
        for t in data.bank[:20]
    ]
    erp_vendors = [
        {
            "name": v.name,
            "paid_ytd": v.total_paid_ytd,
            "pct_spend": v.pct_of_total_spend,
            "linked_bank": v.linked_bank_entity,
        }
        for v in data.erp.vendors
    ]
    gl = [
        {
            "account": g.account,
            "balance": g.balance,
            "outflow_30d": g.projected_30d_outflow,
            "inflow_30d": g.projected_30d_inflow,
        }
        for g in data.erp.gl_snapshots
    ]
    trading = [
        {
            "ticker": p.ticker,
            "qty": p.qty,
            "pnl": round((p.current_price - p.entry_price) * p.qty, 2),
            "order_book_imbalance": p.order_book_imbalance,
            "rsi": p.rsi,
        }
        for p in data.trading
    ]
    news = [
        {"headline": n.headline, "sentiment": n.sentiment, "entities": n.entities}
        for n in data.news[:8]
    ]
    payload = {
        "crm_deals": crm,
        "bank_transactions": bank,
        "erp_vendors": erp_vendors,
        "gl_snapshots": gl,
        "trading_positions": trading,
        "news": news,
        "synced_at": str(data.timestamp),
    }
    return _clip(_dump(payload))


def summarize_blind_spots(output: BlindSpotOutput) -> str:
    spots = [
        {
            "title": b.title,
            "severity": b.severity,
            "estimated_loss": b.estimated_loss,
            "sources": b.connected_sources,
            "description": b.description,
            "confidence": b.confidence,
        }
        for b in output.blind_spots
    ]
    return _clip(_dump({"blind_spots": spots, "count": len(spots)}))


def summarize_attacks(output: AttackOutput) -> str:
    attacks = [
        {
            "name": a.name,
            "type": a.attack_type,
            "target_blind_spot": a.target_blind_spot_id,
            "success_probability": a.success_probability,
            "steps": a.steps,
        }
        for a in output.attacks
    ]
    return _clip(_dump({"attacks": attacks}))


def summarize_tracebacks(output: TracebackOutput) -> str:
    rows: List[dict] = []
    for tb in output.tracebacks:
        rows.append(
            {
                "failures": [f.title for f in tb.similar_failures],
                "losses": [f.dollar_loss for f in tb.similar_failures if f.dollar_loss],
                "path_confidence": tb.connection_probability,
                "blast_radius": tb.blast_radius[:6],
            }
        )
    return _clip(_dump({"tracebacks": rows}))


def summarize_connector(output: ConnectorOutput) -> str:
    syncs = [
        {
            "source": s.source_type,
            "success": s.success,
            "records": s.records_fetched,
            "latency_ms": s.latency_ms,
        }
        for s in output.sync_results
    ]
    connections = [
        {
            "source": c.source_type,
            "state": c.state,
            "data_mode": c.data_mode,
            "message": c.message,
        }
        for c in output.connections
    ]
    return _clip(
        _dump(
            {
                "connections": connections,
                "sync_results": syncs,
                "source_summary": summarize_source_data(output.source_data),
            }
        )
    )


def summarize_decision_signals(signals: Any) -> str:
    return _clip(
        _dump(
            {
                "blind_spots": summarize_blind_spots(signals.silent_finder),
                "attacks": summarize_attacks(signals.adversarial),
                "tracebacks": summarize_tracebacks(signals.traceback),
                "source_data": summarize_source_data(signals.connector.source_data),
            }
        )
    )


def connector_prompt(output: ConnectorOutput) -> str:
    return (
        "Summarize the multi-source sync for a CFO pre-release risk review.\n\n"
        f"Context:\n{summarize_connector(output)}"
    )


def silent_finder_prompt(data: SourceData, blind_spots: Iterable[Any]) -> str:
    spots = list(blind_spots)
    return (
        f"Explain the top cross-source blind spots ({len(spots)} detected) and why they matter "
        "before approving wires or credit.\n\n"
        f"Source data:\n{summarize_source_data(data)}\n\n"
        f"Detected blind spots:\n{_dump([b.model_dump() if hasattr(b, 'model_dump') else b for b in spots])}"
    )


def adversarial_prompt(blind_spot_title: str, blind_spot_body: str) -> str:
    return (
        f"Describe a realistic adversarial exploitation path for this blind spot:\n"
        f"Title: {blind_spot_title}\n"
        f"Details: {blind_spot_body}\n\n"
        "Include which control is bypassed and estimated financial impact."
    )


def adversarial_batch_prompt(output: BlindSpotOutput) -> str:
    return (
        "Stress-test all detected blind spots with adversarial attack narratives.\n\n"
        f"{summarize_blind_spots(output)}"
    )


def traceback_prompt(attack_name: str, failures: Iterable[str]) -> str:
    failure_list = list(failures)
    return (
        f"Link attack '{attack_name}' to historical failures and explain the pattern match.\n\n"
        f"Historical failures: {', '.join(failure_list) or 'none indexed yet'}"
    )


def traceback_batch_prompt(output: AttackOutput) -> str:
    return (
        "Synthesize tracebacks connecting historical failures to current attack patterns.\n\n"
        f"{summarize_attacks(output)}"
    )


def decision_prompt(signals: Any) -> str:
    return (
        "Synthesize final trade, loan, and risk-flag recommendations for CFO sign-off.\n\n"
        f"{summarize_decision_signals(signals)}"
    )


def evolution_prompt(decisions_count: int) -> str:
    return (
        f"Propose conservative weight and rule updates based on {decisions_count} recent decisions. "
        "Note human approval is required before any change is applied."
    )
