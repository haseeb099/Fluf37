"""Unified LLM client with demo mode streaming."""
import asyncio
from typing import AsyncIterator, List, Optional

import structlog

from backend.config import NexusConfig, get_config
from backend.schemas.models import AuditEntry
from backend.utils.audit_log import AuditLog
from backend.utils.errors import LLMError

logger = structlog.get_logger()


def _is_rate_limit_error(exc: Exception) -> bool:
    msg = str(exc).lower()
    return "429" in msg or "rate_limit" in msg or "rate limit" in msg


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
        if not self.config.uses_live_llm():
            if self.config.uses_demo_pipeline():
                demo_text = self._demo_response(agent_id, prompt)
                chunk_size = self.config.max_tokens_per_agent // 50 or 20
                step = min(40, max(20, chunk_size))
                for i in range(0, len(demo_text), step):
                    yield demo_text[i : i + step]
                    await asyncio.sleep(0.002)
                self._audit(agent_id, len(demo_text))
                return
            raise LLMError(
                "Live LLM not configured; set provider API keys and NEXUS_LIVE_LLM=true (demo) "
                "or NEXUS_DEMO_MODE=false",
                model=self.config.active_llm_model(),
            )

        async for token in self._stream_live(
            prompt, system, temperature, max_tokens, agent_id
        ):
            yield token

    async def _stream_openai_compatible(
        self,
        *,
        api_key: str,
        base_url: Optional[str],
        model: str,
        prompt: str,
        system: str,
        temperature: float,
        max_tokens: int,
    ) -> AsyncIterator[str]:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        stream = await client.chat.completions.create(
            model=model,
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
                yield delta

    async def _stream_live(
        self,
        prompt: str,
        system: str,
        temperature: float,
        max_tokens: int,
        agent_id: str,
    ) -> AsyncIterator[str]:
        model = self.config.active_llm_model()
        collected: List[str] = []
        try:
            if self.config.llm_provider in ("openai", "groq"):
                api_key = (
                    self.config.groq_api_key
                    if self.config.llm_provider == "groq"
                    else self.config.openai_api_key
                )
                base_url = self.config.groq_base_url if self.config.llm_provider == "groq" else None
                async for token in self._stream_openai_compatible(
                    api_key=api_key,
                    base_url=base_url,
                    model=model,
                    prompt=prompt,
                    system=system,
                    temperature=temperature,
                    max_tokens=max_tokens,
                ):
                    collected.append(token)
                    yield token
            else:
                from anthropic import AsyncAnthropic

                client = AsyncAnthropic(api_key=self.config.anthropic_api_key)
                async with client.messages.stream(
                    model=model,
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
            if self._should_fallback_to_demo(e):
                async for token in self._stream_demo_fallback(prompt, agent_id):
                    yield token
                return
            raise LLMError(str(e), model=model) from e

        self._audit(agent_id, sum(len(t) for t in collected), model=model)

    def _should_fallback_to_demo(self, exc: Exception) -> bool:
        if not self.config.nexus_llm_fallback_on_error:
            return False
        if not self.config.uses_demo_pipeline():
            return False
        return _is_rate_limit_error(exc)

    async def _stream_demo_fallback(self, prompt: str, agent_id: str) -> AsyncIterator[str]:
        demo_text = self._demo_response(agent_id, prompt)
        logger.info("llm_fallback_demo", agent_id=agent_id)
        step = min(40, max(20, self.config.max_tokens_per_agent // 50 or 20))
        for i in range(0, len(demo_text), step):
            yield demo_text[i : i + step]
            await asyncio.sleep(0.002)
        self._audit(agent_id, len(demo_text), model="demo-fallback")

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

    async def verify_connectivity(self) -> dict:
        """Ping the configured provider with a minimal completion (ignores demo/canned mode)."""
        if not self.config.llm_configured():
            return {"ok": False, "mode": "unconfigured", "error": "Provider API key not set"}
        model = self.config.active_llm_model()
        try:
            parts: List[str] = []
            async for token in self._stream_live(
                "Reply with exactly: Nexus AI connected.",
                "You are a connectivity probe. Reply briefly.",
                0,
                32,
                "connectivity_probe",
            ):
                parts.append(token)
            text = "".join(parts).strip()
            return {
                "ok": bool(text),
                "mode": "live",
                "provider": self.config.llm_provider,
                "model": model,
                "preview": text[:120],
            }
        except LLMError as e:
            return {"ok": False, "mode": "live", "provider": self.config.llm_provider, "error": str(e)}

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
