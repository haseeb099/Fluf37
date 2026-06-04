import pytest
from backend.config import NexusConfig
from backend.memory.layer import MemoryLayer
from backend.schemas.models import MemoryMetadata


@pytest.mark.asyncio
async def test_memory_store_and_search():
    memory = MemoryLayer(NexusConfig(nexus_demo_mode=True))
    await memory.initialize_demo()
    results = await memory.search("circular payment", n=3)
    assert len(results) >= 1
    stats = await memory.get_stats()
    assert stats.vector_count >= 1
    assert stats.graph_nodes >= 1
