"""Build sellable Pre-Release Risk Review artifacts from pipeline output."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional
from uuid import uuid4

from backend.config import NexusConfig
from backend.schemas.models import NexusReport, RiskReviewFinding, RiskReviewReport, RiskReviewSummary, TracebackResult


def _data_mode(config: NexusConfig) -> str:
    if config.uses_demo_pipeline():
        return "synthetic"
    if config.plaid_configured() or config.alpaca_configured():
        return "mixed"
    return "live"


def build_risk_review_report(
    report: NexusReport,
    *,
    config: NexusConfig,
    correlation_id: Optional[str] = None,
) -> RiskReviewReport:
    """Turn NexusReport into a buyer-facing risk review artifact."""
    blind_spots = []
    if report.silent_finder:
        blind_spots = report.silent_finder.blind_spots

    tb_by_bs: dict[str, TracebackResult] = {}
    attacks = report.adversarial.attacks if report.adversarial else []
    tracebacks = report.traceback.tracebacks if report.traceback else []
    for index, attack in enumerate(attacks):
        if index < len(tracebacks):
            tb_by_bs[attack.target_blind_spot_id] = tracebacks[index]

    attacks_by_bs: dict[str, list] = {}
    for attack in attacks:
        attacks_by_bs.setdefault(attack.target_blind_spot_id, []).append(attack)

    findings: List[RiskReviewFinding] = []
    for bs in blind_spots:
        tb = tb_by_bs.get(bs.id)
        related_loss = None
        if tb and tb.similar_failures:
            related_loss = tb.similar_failures[0].title
        bs_attacks = attacks_by_bs.get(bs.id, [])
        stress_passed = all(a.success_probability < 0.65 for a in bs_attacks) if bs_attacks else True
        recommendation = None
        if bs_attacks:
            recommendation = bs_attacks[0].proposed_defense
        elif report.decisions:
            recommendation = report.decisions[0].recommendation
        findings.append(
            RiskReviewFinding(
                id=bs.id,
                title=bs.title,
                severity=bs.severity,
                description=bs.description,
                adversarial_passed=stress_passed,
                related_loss_title=related_loss,
                recommendation=recommendation,
            )
        )

    critical = sum(1 for f in findings if f.severity == "critical")
    high = sum(1 for f in findings if f.severity == "high")
    top_rec = "No material risks detected in this review cycle."
    if report.decisions:
        top_rec = report.decisions[0].recommendation

    summary = RiskReviewSummary(
        review_id=f"rr_{uuid4().hex[:12]}",
        correlation_id=correlation_id,
        status="complete" if report.pipeline_state == "COMPLETE" else "error",
        blind_spots_count=len(findings),
        decisions_count=len(report.decisions),
        critical_count=critical,
        high_count=high,
        top_recommendation=top_rec,
        workflow="pre_release_risk_review",
        data_mode=_data_mode(config),  # type: ignore[arg-type]
        generated_at=datetime.now(timezone.utc),
    )

    return RiskReviewReport(
        summary=summary,
        findings=findings,
        decisions=report.decisions,
        audit_correlation_id=correlation_id,
    )
