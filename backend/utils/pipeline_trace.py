"""Pipeline audit + structured trace events."""
from __future__ import annotations

import time
import uuid
from typing import Optional

import structlog

from backend.schemas.models import AuditEntry
from backend.utils.audit_log import AuditLog

logger = structlog.get_logger()


class PipelineTracer:
    def __init__(
        self,
        tenant_id: str = "default",
        audit: Optional[AuditLog] = None,
        correlation_id: Optional[str] = None,
    ):
        self.tenant_id = tenant_id
        self.audit = audit or AuditLog()
        self.correlation_id = correlation_id or uuid.uuid4().hex[:12]
        self._started_at = time.monotonic()

    def log(self, action: str, preview: str, agent_id: str = "orchestrator", latency_ms: int = 0) -> str:
        entry_hash = self.audit.write(
            AuditEntry(
                agent_id=agent_id,
                action=action,
                payload_preview=preview[:500],
                tenant_id=self.tenant_id,
                latency_ms=latency_ms,
                model="pipeline",
            )
        )
        logger.info(
            "pipeline_trace",
            correlation_id=self.correlation_id,
            tenant_id=self.tenant_id,
            action=action,
            agent_id=agent_id,
            audit_hash=entry_hash[:16],
        )
        return entry_hash

    def pipeline_start(self, mode: str) -> None:
        self.log("pipeline_start", f"mode={mode};correlation={self.correlation_id}")

    def pipeline_state(self, state: str) -> None:
        self.log("pipeline_state", state)

    def agent_complete(self, agent_id: str, summary: str, latency_ms: int = 0) -> None:
        self.log(
            "agent_complete",
            f"{summary};correlation={self.correlation_id}",
            agent_id=agent_id,
            latency_ms=latency_ms,
        )

    def agent_error(self, agent_id: str, detail: str) -> None:
        self.log("agent_error", detail[:200], agent_id=agent_id)

    def pipeline_complete(self, blind_spots: int, decisions: int) -> None:
        elapsed = int((time.monotonic() - self._started_at) * 1000)
        self.log(
            "pipeline_complete",
            f"blind_spots={blind_spots};decisions={decisions};correlation={self.correlation_id}",
            latency_ms=elapsed,
        )

    def pipeline_error(self, reason: str) -> None:
        self.log("pipeline_error", reason)
