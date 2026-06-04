from typing import Any, AsyncIterator

import pytest
from backend.agents.base import BaseAgent
from backend.agents.orchestrator import NexusOrchestrator
from backend.config import NexusConfig
from backend.integration.connection_manager import ConnectionManager
from backend.memory.layer import MemoryLayer
from backend.schemas.models import AgentEvent
from backend.utils.llm_client import LLMClient


class SlowAgent(BaseAgent):
    agent_id = "slow"

    async def run(self, payload: Any) -> AsyncIterator[AgentEvent]:
        import asyncio

        await asyncio.sleep(5)
        yield AgentEvent(type="AGENT_COMPLETE", agent_id=self.agent_id, data={})


@pytest.mark.asyncio
async def test_dispatch_emits_timeout_error():
    config = NexusConfig(nexus_demo_mode=True, agent_timeout_seconds=0)
    memory = MemoryLayer(config)
    mgr = ConnectionManager(config)
    orch = NexusOrchestrator(config, memory, LLMClient(config), mgr)
    orch.agents["slow"] = SlowAgent(config, memory, LLMClient(config))

    events = []
    async for event in orch.dispatch("slow", None):
        events.append(event)

    assert len(events) == 1
    assert events[0].type == "AGENT_ERROR"
    assert events[0].data == "timeout"
