"""Silent Forcing Finder — detect unmeasured variables."""
from typing import AsyncIterator
from uuid import uuid4

from backend.agents.base import AgentState, BaseAgent
from backend.schemas.models import AgentEvent, BlindSpot, BlindSpotOutput, SourceData
from backend.utils.prompt_context import FINANCIAL_ANALYST_SYSTEM, silent_finder_prompt


class SilentForcingFinder(BaseAgent):
    agent_id = "silent_finder"

    async def run(self, payload: SourceData) -> AsyncIterator[AgentEvent]:
        self._set_state(AgentState.RUNNING)
        yield self._emit("AGENT_START", {})
        blind_spots = self._detect_demo_patterns(payload)

        async for event in self._stream_llm(
            silent_finder_prompt(payload, blind_spots),
            system=FINANCIAL_ANALYST_SYSTEM,
        ):
            yield event

        output = BlindSpotOutput(blind_spots=blind_spots)
        yield self._emit("AGENT_COMPLETE", output.model_dump())
        await self.memory.store_agent_output(self.agent_id, output, str(len(blind_spots)) + " blind spots")

    def _detect_demo_patterns(self, data: SourceData) -> list[BlindSpot]:
        spots = []
        # Customer-shareholder overlap
        for deal in data.crm:
            if deal.equity_holders and deal.contact_role == "CFO":
                spots.append(BlindSpot(
                    id=f"bs_{uuid4().hex[:6]}",
                    title="Customer-Shareholder Concentration",
                    description=f"{deal.company}: CFO {deal.contact_name} holds equity — no cap table cross-check rule.",
                    severity="critical",
                    estimated_loss=450000,
                    connected_sources=["crm", "erp"],
                    chain_of_thought=["Cross-reference CRM contacts with equity holders on deals > $100k"],
                    confidence=0.91,
                    counterfactual="If cap table monitoring existed, deal_001 would have been flagged pre-close.",
                ))
        # Cash flow timing
        if data.crm and data.erp.gl_snapshots:
            acme = next((d for d in data.crm if d.company == "Acme Corp"), None)
            if acme and acme.payment_terms_days >= 90:
                spots.append(BlindSpot(
                    id=f"bs_{uuid4().hex[:6]}",
                    title="Cash Flow Timing Mismatch",
                    description="90-day payment terms vs 30-day projected cash gap (-$128k).",
                    severity="high",
                    estimated_loss=128000,
                    connected_sources=["crm", "bank", "erp"],
                    confidence=0.88,
                    counterfactual="Tracking payment_terms vs GL 30-day projection would surface gap.",
                ))
        # Circular payments
        if len(data.bank) >= 3:
            spots.append(BlindSpot(
                id=f"bs_{uuid4().hex[:6]}",
                title="Multi-Hop Circular Payment Detection Gap",
                description="3+ hop circular flows evade 2-entity fraud rules.",
                severity="critical",
                estimated_loss=79000,
                connected_sources=["bank"],
                confidence=0.89,
            ))
        # Order book / RSI
        for pos in data.trading:
            if pos.order_book_imbalance < -0.2 and pos.rsi < 35:
                spots.append(BlindSpot(
                    id=f"bs_{uuid4().hex[:6]}",
                    title="Order Book / RSI Divergence",
                    description=f"{pos.ticker}: sell pressure with oversold RSI — spoofing risk.",
                    severity="high",
                    estimated_loss=21500,
                    connected_sources=["trading", "news"],
                    confidence=0.85,
                ))
        # ERP vendor concentration
        for v in data.erp.vendors:
            if v.pct_of_total_spend > 0.3:
                spots.append(BlindSpot(
                    id=f"bs_{uuid4().hex[:6]}",
                    title="Vendor Concentration Risk",
                    description=f"{v.name} receives {v.pct_of_total_spend:.0%} of spend — unmonitored.",
                    severity="high",
                    estimated_loss=250000,
                    connected_sources=["erp", "bank"],
                    confidence=0.82,
                ))
        # Shell company
        spots.append(BlindSpot(
            id=f"bs_{uuid4().hex[:6]}",
            title="Shell Company Vendor Onboarding",
            description="Nexus Holdings LLC incorporated 3 days ago — no incorporation date check.",
            severity="critical",
            estimated_loss=250000,
            connected_sources=["bank", "erp"],
            confidence=0.90,
        ))
        return spots[:7]
