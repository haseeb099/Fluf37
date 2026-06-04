"""Manages connector connections and sync."""
import asyncio
import time
from typing import Dict, List, Optional

import structlog

from backend.config import NexusConfig
from backend.integration.normalizer import merge_source_data
from backend.integration.registry import ConnectorRegistry
from backend.schemas.models import ConnectionStatus, ConnectorOutput, SourceData, SyncResult, SourceType
from backend.utils.errors import ConnectorError

logger = structlog.get_logger()


class ConnectionManager:
    def __init__(self, config: NexusConfig, tenant_id: str = "default"):
        self.config = config
        self.tenant_id = tenant_id
        self.registry = ConnectorRegistry(config)
        self._connectors: Dict[SourceType, object] = {}

    async def connect(self, source_type: SourceType) -> ConnectionStatus:
        conn = self.registry.create(source_type, self.tenant_id)
        status = await conn.connect()
        self._connectors[source_type] = conn
        return status

    async def disconnect(self, source_type: SourceType) -> None:
        if source_type in self._connectors:
            await self._connectors[source_type].disconnect()
            del self._connectors[source_type]

    async def sync_source(self, source_type: SourceType) -> tuple[SourceData, SyncResult]:
        start = time.monotonic()
        try:
            if source_type not in self._connectors:
                await self.connect(source_type)
            conn = self._connectors[source_type]
            raw = await conn.fetch_batch()
            partial = conn.normalize(raw)
            latency = int((time.monotonic() - start) * 1000)
            count = (
                len(partial.crm) + len(partial.bank) + len(partial.trading)
                + len(partial.news) + len(partial.erp.vendors)
            )
            return partial, SyncResult(
                source_type=source_type,
                success=True,
                records_fetched=count,
                latency_ms=latency,
            )
        except Exception as e:
            logger.error("sync_failed", source=source_type, error=str(e))
            return SourceData(), SyncResult(
                source_type=source_type,
                success=False,
                error=str(e),
                latency_ms=int((time.monotonic() - start) * 1000),
            )

    async def sync_all(self, demo: Optional[bool] = None) -> ConnectorOutput:
        use_demo = demo if demo is not None else self.config.is_demo()
        enabled = self.config.get_enabled_connectors()
        if use_demo:
            enabled = ["crm", "erp", "bank", "trading", "news"]

        tasks = [self.sync_source(st) for st in enabled if st in self.registry.list_types()]  # type: ignore
        results = await asyncio.gather(*tasks)

        partials = []
        sync_results = []
        connections = []
        for partial, sync in results:
            if sync.success:
                partials.append(partial)
            sync_results.append(sync)
            connections.append(
                ConnectionStatus(
                    source_type=sync.source_type,
                    state="connected" if sync.success else "error",
                    message=sync.error,
                )
            )

        merged = merge_source_data(partials) if partials else SourceData()
        return ConnectorOutput(
            source_data=merged,
            connections=connections,
            sync_results=sync_results,
        )

    def get_all_status(self) -> List[ConnectionStatus]:
        statuses = []
        for st in self.config.get_enabled_connectors():
            if st in self._connectors:
                statuses.append(self._connectors[st].get_status())
            else:
                statuses.append(ConnectionStatus(source_type=st, state="disconnected"))  # type: ignore
        return statuses
