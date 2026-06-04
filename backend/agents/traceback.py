"""Traceback agent — RAG + graph."""
from datetime import datetime
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
from backend.utils.synthetic_data import get_demo_failures
from backend.utils.prompt_context import TRACEBACK_SYSTEM, traceback_batch_prompt

_DEMO_FAILURES_BY_ID = {f.id: f for f in get_demo_failures()}


class TracebackAgent(BaseAgent):
    agent_id = "traceback"

    async def run(self, payload: AttackOutput) -> AsyncIterator[AgentEvent]:
        self._set_state(AgentState.RUNNING)
        yield self._emit("AGENT_START", {})
        tracebacks = []
        max_attacks = 1 if self.config.uses_demo_pipeline() else min(3, self.config.traceback_max_results)
        attacks = payload.attacks[:max_attacks]

        async for event in self._stream_llm(
            traceback_batch_prompt(payload),
            system=TRACEBACK_SYSTEM,
        ):
            yield event

        graph = self.memory.get_graph()
        for attack in attacks:
            similar = await self.memory.search(attack.name, n=3)
            failures: list[FailureRecord] = []
            for s in similar:
                fid = s.metadata.failure_id or s.id
                demo = _DEMO_FAILURES_BY_ID.get(fid)
                failures.append(
                    FailureRecord(
                        id=fid,
                        title=demo.title if demo else attack.name,
                        description=demo.description if demo else s.text,
                        source_ids=demo.source_ids if demo else s.metadata.source_ids,
                        affected_entities=demo.affected_entities if demo else [],
                        dollar_loss=demo.dollar_loss if demo else s.metadata.dollar_loss,
                        timestamp=demo.timestamp if demo else datetime.utcnow(),
                        severity=demo.severity if demo else s.metadata.severity,
                    )
                )
            primary_id = failures[0].id if failures else None
            path: list[str] = []
            blast: list[str] = []
            connection_probability = 0.0
            if primary_id and primary_id in graph.graph:
                paths = graph.find_paths(primary_id)
                path = paths[0] if paths else [primary_id]
                blast = sorted(graph.get_blast_radius(primary_id))
                if path and len(path) >= 2:
                    u, v = path[-2], path[-1]
                    edge_data = graph.graph.get_edge_data(u, v) or {}
                    connection_probability = float(edge_data.get("probability", 0.0))

            narrative = (
                f"Historical pattern '{failures[0].title}' matches attack '{attack.name}' "
                f"with {int(connection_probability * 100)}% path confidence."
                if failures and connection_probability
                else f"Linked {len(failures)} historical incident(s) to attack '{attack.name}'."
            )
            tracebacks.append(TracebackResult(
                similar_failures=failures,
                graph_path=path,
                connection_probability=connection_probability or (0.75 if failures else 0.0),
                rule_update_recommendations=[
                    "Enable 7-hop graph traversal on payment flows",
                    "Cross-reference CRM equity with vendor payments",
                ],
                timeline=[
                    TimelineEvent(
                        date=f.timestamp.strftime("%Y-%m-%d") if hasattr(f.timestamp, "strftime") else "2026-03-15",
                        event=f.title or f.description[:80],
                        severity=f.severity,
                    )
                    for f in failures[:3]
                ]
                or [
                    TimelineEvent(date="2026-03-15", event="Circular payment loss $79k", severity="critical"),
                ],
                blast_radius=blast,
                narrative=narrative,
            ))

        output = TracebackOutput(tracebacks=tracebacks)
        yield self._emit("AGENT_COMPLETE", output.model_dump())
