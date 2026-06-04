"""Memory layer facade."""
from typing import List

from pydantic import BaseModel

from backend.config import NexusConfig
from backend.memory.demo_graph import seed_demo_graph
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
        if not self._seeded:
            for f in get_demo_failures():
                await self.vector.store(
                    f.description,
                    MemoryMetadata(
                        agent_id="traceback",
                        failure_id=f.id,
                        severity=f.severity,
                        source_ids=f.source_ids,
                        source_types=f.source_ids,
                        timestamp=f.timestamp.isoformat(),
                        dollar_loss=f.dollar_loss,
                    ),
                )
            self._seeded = True
        if self.config.uses_demo_pipeline():
            seed_demo_graph(self.graph)

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
