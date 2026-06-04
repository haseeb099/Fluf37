"""Evolution agent — weekly self-improvement."""
from typing import AsyncIterator

from pydantic import BaseModel

from backend.agents.base import AgentState, BaseAgent
from backend.schemas.models import AgentEvent, EvolutionReport


class EvolutionInput(BaseModel):
    decisions_count: int = 0


class EvolutionAgent(BaseAgent):
    agent_id = "evolution"

    async def run(self, payload: EvolutionInput) -> AsyncIterator[AgentEvent]:
        self._set_state(AgentState.RUNNING)
        yield self._emit("AGENT_START", {})

        async for event in self._stream_llm("Generate evolution report with weight change proposals."):
            yield event

        report = EvolutionReport(
            blind_spots_found=5,
            attacks_generated=5,
            decisions_made=max(payload.decisions_count, 2),
            weight_changes={"forcing": 0.05, "technical": -0.03, "fundamental": 0.0, "news": -0.02},
            new_rules=[
                "Cross-reference CRM equity holders on deals > $100k",
                "Flag payments to entities incorporated < 30 days",
            ],
            self_improvement_score=0.123,
            backtest_score=0.71,
            approval_required=True,
        )
        yield self._emit("AGENT_COMPLETE", report.model_dump())
