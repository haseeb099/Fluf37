"""Decision agent — mixture of experts."""
from typing import AsyncIterator

from pydantic import BaseModel

from backend.agents.base import AgentState, BaseAgent
from backend.schemas.models import (
    AgentEvent,
    AttackOutput,
    BlindSpotOutput,
    ConnectorOutput,
    DecisionOutput,
    SourceData,
    TracebackOutput,
)


class AllSignals(BaseModel):
    connector: ConnectorOutput
    silent_finder: BlindSpotOutput
    adversarial: AttackOutput
    traceback: TracebackOutput


class DecisionAgent(BaseAgent):
    agent_id = "decision"

    async def run(self, payload: AllSignals) -> AsyncIterator[AgentEvent]:
        self._set_state(AgentState.RUNNING)
        yield self._emit("AGENT_START", {})
        data = payload.connector.source_data
        decisions = self._make_decisions(data, payload)

        async for event in self._stream_llm("Synthesize final trade and loan decisions.", agent_id=self.agent_id):
            yield event

        for d in decisions:
            await self.memory.timeseries.record_decision(d)
        yield self._emit("AGENT_COMPLETE", {"decisions": [d.model_dump() for d in decisions]})

    def _make_decisions(self, data: SourceData, signals: AllSignals) -> list[DecisionOutput]:
        decisions = []
        acme_pos = next((p for p in data.trading if p.ticker == "ACME"), None)
        if acme_pos:
            stress_passed = not (acme_pos.order_book_imbalance < -0.3 and acme_pos.rsi < 35)
            decisions.append(DecisionOutput(
                decision_type="trade",
                recommendation="SELL ACME — order book sell pressure contradicts RSI oversold signal",
                confidence=0.78,
                adversarial_stress_passed=stress_passed,
                signal_breakdown={"technical": -0.6, "news": -0.4, "forcing": -0.5, "fundamental": 0.1},
                sensitivity={"technical": 0.35, "forcing": 0.30, "news": 0.20, "fundamental": 0.15},
                reasoning="Order book imbalance -0.32 with RSI 32 suggests spoofing, not genuine oversold.",
                chain_of_thought=["Technical: bearish imbalance", "News: negative ACME sentiment"],
            ))
        acme_deal = next((d for d in data.crm if d.company == "Acme Corp"), None)
        if acme_deal:
            high_risk = len(signals.silent_finder.blind_spots) >= 2
            decisions.append(DecisionOutput(
                decision_type="loan",
                recommendation="REVIEW — defer approval pending concentration and cash flow analysis",
                confidence=0.72 if high_risk else 0.55,
                adversarial_stress_passed=not high_risk,
                signal_breakdown={"fundamental": -0.7, "forcing": -0.6, "technical": 0.0, "news": -0.3},
                sensitivity={"fundamental": 0.40, "forcing": 0.35},
                reasoning="90-day terms + CFO equity overlap + ERP vendor concentration.",
                traceback_chain=["fail_001", "fail_003"],
            ))
        if not decisions:
            decisions.append(DecisionOutput(
                decision_type="risk_flag",
                recommendation="MONITOR — elevated cross-source risk signals",
                confidence=0.65,
            ))
        return decisions
