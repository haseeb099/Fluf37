"""Unified LLM client with demo mode streaming."""
import asyncio
from typing import AsyncIterator, List, Optional

import structlog

from backend.config import NexusConfig, get_config
from backend.utils.audit_log import AuditLog
from backend.utils.errors import LLMError
from backend.schemas.models import AuditEntry

logger = structlog.get_logger()


class LLMClient:
    def __init__(self, config: Optional[NexusConfig] = None, audit: Optional[AuditLog] = None):
        self.config = config or get_config()
        self.audit = audit or AuditLog()

    async def stream(
        self,
        prompt: str,
        system: str = "",
        temperature: float = 0.3,
        max_tokens: int = 2048,
        agent_id: str = "unknown",
    ) -> AsyncIterator[str]:
        if self.config.is_demo():
            demo_text = self._demo_response(agent_id, prompt)
            for i in range(0, len(demo_text), self.config.max_tokens_per_agent // 50 or 20):
                chunk = demo_text[i : i + 20]
                yield chunk
                await asyncio.sleep(0.01)
            self._audit(agent_id, len(demo_text))
            return
        raise LLMError("Live LLM not configured; set NEXUS_DEMO_MODE=true", model=self.config.primary_model)

    async def complete(
        self,
        prompt: str,
        system: str = "",
        temperature: float = 0.3,
        agent_id: str = "unknown",
    ) -> str:
        parts = []
        async for token in self.stream(prompt, system, temperature, agent_id=agent_id):
            parts.append(token)
        return "".join(parts)

    def _demo_response(self, agent_id: str, prompt: str) -> str:
        responses = {
            "silent_finder": "Analyzing cross-source gaps: CRM payment terms vs bank cash flow vs ERP vendor concentration reveal unmeasured concentration risk.",
            "adversarial": "Attack path: exploit 3-hop circular payment detection blind spot via shell entity registration.",
            "traceback": "Historical match: March 2026 circular payment incident linked with 0.87 confidence.",
            "decision": "Recommendation: REVIEW loan exposure; SELL ACME on order book/RSI divergence. Adversarial stress: marginal pass.",
            "evolution": "Self-improvement +12.3% week-over-week. Proposed weight shift: forcing +0.05, technical -0.03.",
            "connector": "All sources synchronized. CRM, ERP, bank, trading, news merged.",
        }
        return responses.get(agent_id, f"Demo analysis for {agent_id}.")

    def _audit(self, agent_id: str, tokens: int) -> None:
        self.audit.write(
            AuditEntry(
                agent_id=agent_id,
                action="llm_complete",
                payload_preview="demo",
                tokens=tokens,
                latency_ms=50,
                model="demo",
            )
        )
