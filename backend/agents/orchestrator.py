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
from backend.utils.pipeline_trace import PipelineTracer

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

    async def _emit_pipeline_state(
        self, state: PipelineState, tracer: Optional[PipelineTracer] = None
    ) -> AgentEvent:
        self.pipeline_state = state
        if tracer:
            tracer.pipeline_state(state)
        data: Dict[str, Any] = {"state": state}
        if tracer:
            data["correlation_id"] = tracer.correlation_id
        return AgentEvent(type="PIPELINE_STATE", agent_id="orchestrator", data=data)

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

    async def _run_agent(
        self,
        agent_id: str,
        payload: Any,
        tracer: PipelineTracer,
    ) -> AsyncIterator[AgentEvent]:
        async for event in self.dispatch(agent_id, payload):
            if event.type == "AGENT_ERROR":
                tracer.agent_error(agent_id, str(event.data))
            yield event

    async def run_pipeline(
        self, mode: str = "demo", tenant_id: str = "default"
    ) -> AsyncIterator[AgentEvent]:
        tracer = PipelineTracer(tenant_id=tenant_id)
        tracer.pipeline_start(mode)
        yield await self._emit_pipeline_state("CONNECTING", tracer)

        connector_output = None
        async for event in self._run_agent("connector", None, tracer):
            yield event
            if event.type == "AGENT_COMPLETE":
                from backend.schemas.models import ConnectorOutput
                connector_output = ConnectorOutput.model_validate(event.data)
                self.context["connector"] = connector_output
                tracer.agent_complete("connector", f"sources={len(connector_output.connections)}")

        if not connector_output:
            tracer.pipeline_error("connector_failed")
            yield await self._emit_pipeline_state("ERROR", tracer)
            return

        yield await self._emit_pipeline_state("ANALYZING", tracer)
        async for event in self._run_agent("silent_finder", connector_output.source_data, tracer):
            yield event
            if event.type == "AGENT_COMPLETE":
                from backend.schemas.models import BlindSpotOutput
                out = BlindSpotOutput.model_validate(event.data)
                self.context["silent_finder"] = out
                tracer.agent_complete("silent_finder", f"count={len(out.blind_spots)}")

        yield await self._emit_pipeline_state("ATTACKING", tracer)
        async for event in self._run_agent("adversarial", self.context["silent_finder"], tracer):
            yield event
            if event.type == "AGENT_COMPLETE":
                from backend.schemas.models import AttackOutput
                out = AttackOutput.model_validate(event.data)
                self.context["adversarial"] = out
                tracer.agent_complete("adversarial", f"attacks={len(out.attacks)}")

        yield await self._emit_pipeline_state("TRACING", tracer)
        async for event in self._run_agent("traceback", self.context["adversarial"], tracer):
            yield event
            if event.type == "AGENT_COMPLETE":
                from backend.schemas.models import TracebackOutput
                out = TracebackOutput.model_validate(event.data)
                self.context["traceback"] = out
                tracer.agent_complete("traceback", f"matches={len(out.tracebacks)}")

        yield await self._emit_pipeline_state("DECIDING", tracer)
        signals = AllSignals(
            connector=self.context["connector"],
            silent_finder=self.context["silent_finder"],
            adversarial=self.context["adversarial"],
            traceback=self.context["traceback"],
        )
        async for event in self._run_agent("decision", signals, tracer):
            yield event
            if event.type == "AGENT_COMPLETE" and isinstance(event.data, dict) and "decisions" in event.data:
                from backend.schemas.models import DecisionOutput
                decisions = [DecisionOutput.model_validate(d) for d in event.data["decisions"]]
                self.context["decisions"] = decisions
                tracer.agent_complete("decision", f"decisions={len(decisions)}")

        yield await self._emit_pipeline_state("EVOLVING", tracer)
        count = len(self.context.get("decisions", []))
        async for event in self._run_agent("evolution", EvolutionInput(decisions_count=count), tracer):
            yield event
            if event.type == "AGENT_COMPLETE":
                from backend.schemas.models import EvolutionReport
                self.context["evolution"] = EvolutionReport.model_validate(event.data)
                tracer.agent_complete("evolution", "report_ready")

        sf = self.context.get("silent_finder")
        bs = len(sf.blind_spots) if sf else 0
        tracer.pipeline_complete(bs, count)
        yield await self._emit_pipeline_state("COMPLETE", tracer)

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
