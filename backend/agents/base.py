"""Base agent with streaming events."""
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, AsyncIterator, ClassVar, Optional

import structlog
from pydantic import BaseModel

from backend.config import NexusConfig
from backend.memory.layer import MemoryLayer
from backend.schemas.models import AgentEvent
from backend.utils.llm_client import LLMClient

logger = structlog.get_logger()


class AgentState(str, Enum):
    WAITING = "waiting"
    DISPATCHED = "dispatched"
    RUNNING = "running"
    STREAMING = "streaming"
    COMPLETE = "complete"
    ERROR = "error"


class BaseAgent(ABC):
    agent_id: ClassVar[str] = "base"
    state: AgentState = AgentState.WAITING

    def __init__(self, config: NexusConfig, memory: MemoryLayer, llm: LLMClient):
        self.config = config
        self.memory = memory
        self.llm = llm
        self.log = structlog.get_logger(agent_id=self.agent_id)

    @abstractmethod
    async def run(self, payload: BaseModel) -> AsyncIterator[AgentEvent]:
        ...

    async def run_demo(self, payload: Optional[BaseModel] = None) -> AsyncIterator[AgentEvent]:
        async for event in self.run(payload):  # type: ignore
            yield event

    def _emit(self, event_type: str, data: Any) -> AgentEvent:
        return AgentEvent(type=event_type, agent_id=self.agent_id, data=data)  # type: ignore

    def _set_state(self, state: AgentState) -> None:
        self.state = state

    async def _stream_llm(self, prompt: str, system: str = "", temperature: float = 0.3) -> AsyncIterator[AgentEvent]:
        self._set_state(AgentState.STREAMING)
        try:
            async for token in self.llm.stream(prompt, system, temperature, agent_id=self.agent_id):
                yield self._emit("AGENT_TOKEN", token)
        except Exception as e:
            self._set_state(AgentState.ERROR)
            yield self._emit("AGENT_ERROR", str(e))
            return
        self._set_state(AgentState.COMPLETE)
