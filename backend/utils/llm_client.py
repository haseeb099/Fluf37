"""Unified LLM client with demo mode streaming."""
import asyncio
from typing import AsyncIterator, List, Optional

import structlog

from backend.config import NexusConfig, get_config
from backend.schemas.models import AuditEntry
from backend.utils.audit_log import AuditLog
from backend.utils.errors import LLMError

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
            chunk_size = self.config.max_tokens_per_agent // 50 or 20
            step = min(40, max(20, chunk_size))
            for i in range(0, len(demo_text), step):
                yield demo_text[i : i + step]
                await asyncio.sleep(0.002)
            self._audit(agent_id, len(demo_text))
            return

        if not self.config.llm_configured():
            raise LLMError(
                "Live LLM not configured; set API keys or NEXUS_DEMO_MODE=true",
                model=self.config.primary_model,
            )

        async for token in self._stream_live(
            prompt, system, temperature, max_tokens, agent_id
        ):
            yield token

    async def _stream_live(
        self,
        prompt: str,
        system: str,
        temperature: float,
        max_tokens: int,
        agent_id: str,
    ) -> AsyncIterator[str]:
        model = self.config.primary_model
        collected: List[str] = []
        try:
            if self.config.llm_provider == "openai":
                from openai import AsyncOpenAI

                client = AsyncOpenAI(api_key=self.config.openai_api_key)
                stream = await client.chat.completions.create(
                    model=self.config.fallback_model,
                    messages=[
                        {"role": "system", "content": system or "You are Nexus AI."},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=True,
                    timeout=self.config.agent_timeout_seconds,
                )
                async for chunk in stream:
                    delta = chunk.choices[0].delta.content or ""
                    if delta:
                        collected.append(delta)
                        yield delta
                model = self.config.fallback_model
            else:
                from anthropic import AsyncAnthropic

                client = AsyncAnthropic(api_key=self.config.anthropic_api_key)
                async with client.messages.stream(
                    model=self.config.primary_model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    system=system or "You are Nexus AI.",
                    messages=[{"role": "user", "content": prompt}],
                    timeout=self.config.agent_timeout_seconds,
                ) as stream:
                    async for text in stream.text_stream:
                        collected.append(text)
                        yield text
        except Exception as e:
            logger.warning("llm_live_failed", agent_id=agent_id, error=str(e))
            raise LLMError(str(e), model=model) from e

        self._audit(agent_id, sum(len(t) for t in collected), model=model)

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

    def _audit(self, agent_id: str, tokens: int, model: str = "demo") -> None:
        self.audit.write(
            AuditEntry(
                agent_id=agent_id,
                action="llm_complete",
                payload_preview="demo" if model == "demo" else "live",
                tokens=tokens,
                latency_ms=50,
                model=model,
            )
        )
