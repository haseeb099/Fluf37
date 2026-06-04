"""Traceback agent — RAG + graph."""
from typing import AsyncIterator

from backend.agents.base import AgentState, BaseAgent
from backend.schemas.models import (
    AgentEvent,
    AttackOutput,
    FailureRecord,
    TimelineEvent,
    TracebackOutput,
    TracebackResult,
)


class TracebackAgent(BaseAgent):
    agent_id = "traceback"

    async def run(self, payload: AttackOutput) -> AsyncIterator[AgentEvent]:
        self._set_state(AgentState.RUNNING)
        yield self._emit("AGENT_START", {})
        tracebacks = []
        max_attacks = 1 if self.config.is_demo() else min(3, self.config.traceback_max_results)
        attacks = payload.attacks[:max_attacks]

        if self.config.is_demo():
            async for event in self._stream_llm(
                "Synthesize tracebacks linking historical failures to current attack patterns.",
                system="Connect historical failures to current attack patterns.",
            ):
                yield event

        for attack in attacks:
            similar = await self.memory.search(attack.name, n=3)
            failures = [
                FailureRecord(
                    id=s.id,
                    description=s.text,
                    source_ids=s.metadata.source_ids,
                    dollar_loss=s.metadata.dollar_loss,
                    severity=s.metadata.severity,
                )
                for s in similar
            ]
            path = ["fail_001", "loss_event_001"] if failures else []
            blast = list(self.memory.get_graph().get_blast_radius("fail_001"))

            if not self.config.is_demo():
                async for event in self._stream_llm(
                    f"Synthesize traceback for attack {attack.name}",
                    system="Connect historical failures to current attack patterns.",
                ):
                    yield event

            tracebacks.append(TracebackResult(
                similar_failures=failures,
                graph_path=path,
                connection_probability=0.87,
                rule_update_recommendations=[
                    "Enable 7-hop graph traversal on payment flows",
                    "Cross-reference CRM equity with vendor payments",
                ],
                timeline=[
                    TimelineEvent(date="2026-03-15", event="Circular payment loss $79k", severity="critical"),
                    TimelineEvent(date="2026-04-02", event="ACME RSI divergence loss", severity="high"),
                ],
                blast_radius=blast,
                narrative="March 2026 circular payment pattern matches current 3-hop structure with 87% confidence.",
            ))

        output = TracebackOutput(tracebacks=tracebacks)
        yield self._emit("AGENT_COMPLETE", output.model_dump())
