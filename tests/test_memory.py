import pytest
from backend.config import NexusConfig
from backend.memory.layer import MemoryLayer
from backend.memory.vector import VectorMemory
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


@pytest.mark.asyncio
async def test_vector_search_ranked_subset_not_all_docs():
    config = NexusConfig(nexus_demo_mode=True)
    vec = VectorMemory(config)
    await vec.store(
        "vendor concentration ERP mismatch",
        MemoryMetadata(agent_id="traceback", severity="high"),
    )
    await vec.store(
        "unrelated weather forecast data",
        MemoryMetadata(agent_id="traceback", severity="low"),
    )
    await vec.store(
        "payment circular flow detection gap",
        MemoryMetadata(agent_id="traceback", severity="critical"),
    )
    results = await vec.search("circular payment vendor", n_results=2)
    assert len(results) == 2
    assert len(results) < 3
    texts = [r.text.lower() for r in results]
    assert any("circular" in t or "payment" in t or "vendor" in t for t in texts)
    assert results[0].score >= results[-1].score
