"""Connector agent — multi-source data sync."""
from typing import AsyncIterator

from pydantic import BaseModel

from backend.agents.base import AgentState, BaseAgent
from backend.integration.connection_manager import ConnectionManager
from backend.schemas.models import AgentEvent


class ConnectorAgent(BaseAgent):
    agent_id = "connector"

    def __init__(self, config, memory, llm, connection_manager: ConnectionManager):
        super().__init__(config, memory, llm)
        self.connection_manager = connection_manager

    async def run(self, payload: BaseModel | None = None) -> AsyncIterator[AgentEvent]:
        self._set_state(AgentState.RUNNING)
        yield self._emit("AGENT_START", {})

        enabled = self.config.get_enabled_connectors()
        for source in enabled:
            yield AgentEvent(
                type="SOURCE_SYNC_START",
                agent_id=self.agent_id,
                data={"source": source},
            )

        output = await self.connection_manager.sync_all(demo=self.config.is_demo())

        for sync in output.sync_results:
            yield AgentEvent(
                type="SOURCE_SYNC_COMPLETE",
                agent_id=self.agent_id,
                data=sync.model_dump(),
            )

        async for event in self._stream_llm("Summarize multi-source sync status."):
            yield event

        yield self._emit("AGENT_COMPLETE", output.model_dump())
        await self.memory.store_agent_output(self.agent_id, output, "connector sync complete")
