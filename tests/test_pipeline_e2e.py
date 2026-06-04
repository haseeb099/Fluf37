import pytest
from backend.agents.orchestrator import NexusOrchestrator
from backend.config import NexusConfig
from backend.integration.connection_manager import ConnectionManager
from backend.memory.layer import MemoryLayer
from backend.utils.llm_client import LLMClient


@pytest.mark.asyncio
async def test_full_pipeline_demo():
    config = NexusConfig(nexus_demo_mode=True)
    memory = MemoryLayer(config)
    await memory.initialize_demo()
    mgr = ConnectionManager(config)
    llm = LLMClient(config)
    orch = NexusOrchestrator(config, memory, llm, mgr)

    completes = []
    async for event in orch.run_pipeline("demo"):
        if event.type == "AGENT_COMPLETE":
            completes.append(event.agent_id)

    assert "connector" in completes
    assert "silent_finder" in completes
    assert "adversarial" in completes
    assert "traceback" in completes
    assert "decision" in completes
    assert "evolution" in completes
    assert orch.pipeline_state == "COMPLETE"
    report = orch.aggregate_results()
    assert report.silent_finder is not None
    assert len(report.silent_finder.blind_spots) >= 3
    assert len(report.adversarial.attacks) >= 3
    assert len(report.decisions) >= 1
