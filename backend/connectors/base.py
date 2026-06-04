"""Base connector interface."""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, Optional

from backend.config import NexusConfig
from backend.schemas.models import ConnectionStatus, SourceData, SourceType


class BaseConnector(ABC):
    source_type: SourceType
    supports_webhook: bool = False

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

    def get_status(self) -> ConnectionStatus:
        freshness = None
        if self._last_sync:
            freshness = (datetime.utcnow() - self._last_sync).total_seconds()
        return ConnectionStatus(
            source_type=self.source_type,
            state="connected" if self._connected else "disconnected",
            last_sync=self._last_sync,
            freshness_seconds=freshness,
        )
