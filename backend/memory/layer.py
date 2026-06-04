"""Memory layer facade."""
from typing import List

from pydantic import BaseModel

from backend.config import NexusConfig
from backend.memory.graph import NexusGraph
from backend.memory.timeseries import TimeSeriesMemory
from backend.memory.vector import VectorMemory
from backend.schemas.models import MemoryMetadata, MemoryResult, MemoryStats
from backend.utils.synthetic_data import get_demo_failures


class MemoryLayer:
    def __init__(self, config: NexusConfig):
        self.config = config
        self.vector = VectorMemory(config)
        self.graph = NexusGraph(config)
        self.timeseries = TimeSeriesMemory(config)
        self._seeded = False

    async def initialize_demo(self) -> None:
        if self._seeded:
            return
        for f in get_demo_failures():
            await self.vector.store(
                f.description,
                MemoryMetadata(
                    agent_id="traceback",
                    severity=f.severity,
                    source_ids=f.source_ids,
                    source_types=f.source_ids,
                    timestamp=f.timestamp.isoformat(),
                    dollar_loss=f.dollar_loss,
                ),
            )
            self.graph.add_node(f.id, "failure", {"description": f.description, "severity": f.severity})
        self.graph.add_node("loss_event_001", "loss_event", {"dollar_loss": 79000})
        self.graph.add_edge("fail_001", "loss_event_001", "leads_to", 0.87)
        self.graph.save()
        self._seeded = True

    async def store_agent_output(self, agent_id: str, output: BaseModel, text_repr: str) -> None:
        await self.vector.store(
            text_repr,
            MemoryMetadata(agent_id=agent_id, source_ids=[], source_types=[]),
        )

    async def search(self, query: str, n: int = 5) -> List[MemoryResult]:
        return await self.vector.search(query, n)

    def get_graph(self) -> NexusGraph:
        return self.graph

    async def get_stats(self) -> MemoryStats:
        decisions = await self.timeseries.get_decisions()
        g = self.graph.graph
        return MemoryStats(
            vector_count=await self.vector.get_stats(),
            graph_nodes=g.number_of_nodes(),
            graph_edges=g.number_of_edges(),
            decisions_count=len(decisions),
        )
