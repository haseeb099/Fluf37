"""Nexus orchestrator — pipeline conductor."""
import asyncio
from typing import Any, AsyncIterator, Dict, List, Optional

import structlog

from backend.agents.adversarial import AdversarialRedTeam
from backend.agents.base import BaseAgent
from backend.agents.connector_agent import ConnectorAgent
from backend.agents.decision import AllSignals, DecisionAgent
from backend.agents.evolution import EvolutionAgent, EvolutionInput
from backend.agents.silent_finder import SilentForcingFinder
from backend.agents.traceback import TracebackAgent
from backend.config import NexusConfig
from backend.integration.connection_manager import ConnectionManager
from backend.memory.layer import MemoryLayer
from backend.schemas.models import AgentEvent, NexusReport, PipelineState
from backend.utils.llm_client import LLMClient

logger = structlog.get_logger()


class WebSocketManager:
    def __init__(self):
        self.connections: List[Any] = []

    async def broadcast(self, event: AgentEvent) -> None:
        pass  # wired in main.py


class NexusOrchestrator:
    def __init__(
        self,
        config: NexusConfig,
        memory: MemoryLayer,
        llm: LLMClient,
        connection_manager: ConnectionManager,
        ws_manager: Optional[WebSocketManager] = None,
    ):
        self.config = config
        self.memory = memory
        self.llm = llm
        self.connection_manager = connection_manager
        self.ws = ws_manager or WebSocketManager()
        self.context: Dict[str, Any] = {}
        self.pipeline_state: PipelineState = "IDLE"

        self.agents: Dict[str, BaseAgent] = {
            "connector": ConnectorAgent(config, memory, llm, connection_manager),
            "silent_finder": SilentForcingFinder(config, memory, llm),
            "adversarial": AdversarialRedTeam(config, memory, llm),
            "traceback": TracebackAgent(config, memory, llm),
            "decision": DecisionAgent(config, memory, llm),
            "evolution": EvolutionAgent(config, memory, llm),
        }

    async def _emit_pipeline_state(self, state: PipelineState) -> AgentEvent:
        self.pipeline_state = state
        return AgentEvent(type="PIPELINE_STATE", agent_id="orchestrator", data={"state": state})

    async def dispatch(self, agent_id: str, payload: Any) -> AsyncIterator[AgentEvent]:
        agent = self.agents[agent_id]
        timeout = self.config.agent_timeout_seconds
        try:
            agen = agent.run(payload)
            while True:
                try:
                    event = await asyncio.wait_for(agen.__anext__(), timeout=timeout)
                except StopAsyncIteration:
                    break
                yield event
        except asyncio.TimeoutError:
            yield AgentEvent(type="AGENT_ERROR", agent_id=agent_id, data="timeout")
        except Exception as e:
            logger.exception("agent_failed", agent_id=agent_id)
            yield AgentEvent(type="AGENT_ERROR", agent_id=agent_id, data=str(e))

    async def run_pipeline(self, mode: str = "demo") -> AsyncIterator[AgentEvent]:
        yield await self._emit_pipeline_state("CONNECTING")

        connector_output = None
        async for event in self.dispatch("connector", None):
            yield event
            if event.type == "AGENT_COMPLETE":
                from backend.schemas.models import ConnectorOutput
                connector_output = ConnectorOutput.model_validate(event.data)
                self.context["connector"] = connector_output

        if not connector_output:
            yield await self._emit_pipeline_state("ERROR")
            return

        yield await self._emit_pipeline_state("ANALYZING")
        async for event in self.dispatch("silent_finder", connector_output.source_data):
            yield event
            if event.type == "AGENT_COMPLETE":
                from backend.schemas.models import BlindSpotOutput
                self.context["silent_finder"] = BlindSpotOutput.model_validate(event.data)

        yield await self._emit_pipeline_state("ATTACKING")
        async for event in self.dispatch("adversarial", self.context["silent_finder"]):
            yield event
            if event.type == "AGENT_COMPLETE":
                from backend.schemas.models import AttackOutput
                self.context["adversarial"] = AttackOutput.model_validate(event.data)

        yield await self._emit_pipeline_state("TRACING")
        async for event in self.dispatch("traceback", self.context["adversarial"]):
            yield event
            if event.type == "AGENT_COMPLETE":
                from backend.schemas.models import TracebackOutput
                self.context["traceback"] = TracebackOutput.model_validate(event.data)

        yield await self._emit_pipeline_state("DECIDING")
        signals = AllSignals(
            connector=self.context["connector"],
            silent_finder=self.context["silent_finder"],
            adversarial=self.context["adversarial"],
            traceback=self.context["traceback"],
        )
        async for event in self.dispatch("decision", signals):
            yield event
            if event.type == "AGENT_COMPLETE" and isinstance(event.data, dict) and "decisions" in event.data:
                from backend.schemas.models import DecisionOutput
                self.context["decisions"] = [DecisionOutput.model_validate(d) for d in event.data["decisions"]]

        yield await self._emit_pipeline_state("EVOLVING")
        count = len(self.context.get("decisions", []))
        async for event in self.dispatch("evolution", EvolutionInput(decisions_count=count)):
            yield event
            if event.type == "AGENT_COMPLETE":
                from backend.schemas.models import EvolutionReport
                self.context["evolution"] = EvolutionReport.model_validate(event.data)

        yield await self._emit_pipeline_state("COMPLETE")

    def aggregate_results(self) -> NexusReport:
        return NexusReport(
            connector=self.context.get("connector"),
            silent_finder=self.context.get("silent_finder"),
            adversarial=self.context.get("adversarial"),
            traceback=self.context.get("traceback"),
            decisions=self.context.get("decisions", []),
            evolution=self.context.get("evolution"),
            pipeline_state=self.pipeline_state,
        )
