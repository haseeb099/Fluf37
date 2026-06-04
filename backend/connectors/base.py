"""Base connector interface."""
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, Optional

from backend.config import NexusConfig
from backend.integration.capabilities import peek_data_mode
from backend.schemas.models import ConnectionStatus, DataMode, SourceData, SourceType


class BaseConnector(ABC):
    source_type: SourceType
    supports_webhook: bool = False
    live_vendor: ClassVar[Optional[str]] = None

    def __init__(self, config: NexusConfig, tenant_id: str = "default"):
        self.config = config
        self.tenant_id = tenant_id
        self._connected = False
        self._last_sync: Optional[datetime] = None

    @abstractmethod
    async def connect(self) -> ConnectionStatus:
        ...

    @abstractmethod
    async def disconnect(self) -> None:
        ...

    @abstractmethod
    async def fetch_batch(self) -> Dict[str, Any]:
        ...

    @abstractmethod
    def normalize(self, raw: Dict[str, Any]) -> SourceData:
        ...

    async def health_check(self) -> bool:
        return self._connected

    def resolve_data_mode(self) -> DataMode:
        return peek_data_mode(self.config, self.source_type, self.live_vendor)

    def status_message(self, mode: DataMode) -> Optional[str]:
        if mode == "demo":
            return "Synthetic demo data (deterministic seed)"
        if mode == "stub":
            vendor = self.live_vendor or self.source_type
            return f"Live {vendor} not configured — enable flag + credentials"
        if mode == "empty":
            return "Live enabled; vendor API integration returns empty (not shipped)"
        if mode == "live":
            return f"Live {self.live_vendor or self.source_type} fetch"
        return None

    def get_status(self) -> ConnectionStatus:
        freshness = None
        if self._last_sync:
            now = datetime.now(timezone.utc)
            last = self._last_sync
            if last.tzinfo is None:
                last = last.replace(tzinfo=timezone.utc)
            freshness = (now - last).total_seconds()
        mode = self.resolve_data_mode()
        return ConnectionStatus(
            source_type=self.source_type,
            state="connected" if self._connected else "disconnected",
            last_sync=self._last_sync,
            freshness_seconds=freshness,
            data_mode=mode,
            live_vendor=self.live_vendor,
            message=self.status_message(mode),
        )
