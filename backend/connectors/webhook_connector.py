from datetime import datetime
from typing import Any, Dict

from backend.connectors.base import BaseConnector
from backend.schemas.models import BankTransaction, ConnectionStatus, CRMDeal, SourceData


class WebhookConnector(BaseConnector):
    """Normalizes pushed webhook payloads per source."""

    def __init__(self, config, tenant_id: str = "default", source_type: str = "bank"):
        super().__init__(config, tenant_id)
        self.source_type = source_type  # type: ignore
        self.supports_webhook = True
        self._buffer: Dict[str, Any] = {}

    async def connect(self) -> ConnectionStatus:
        self._connected = True
        return self.get_status()

    async def disconnect(self) -> None:
        self._connected = False

    def ingest(self, payload: Dict[str, Any]) -> None:
        self._buffer = payload
        self._last_sync = datetime.utcnow()

    async def fetch_batch(self) -> Dict[str, Any]:
        return self._buffer

    def normalize(self, raw: Dict[str, Any]) -> SourceData:
        if self.source_type == "bank":
            txs = [BankTransaction(**t) for t in raw.get("transactions", [])]
            return SourceData(bank=txs, source_ids=["bank"])
        if self.source_type == "crm":
            deals = [CRMDeal(**d) for d in raw.get("deals", [])]
            return SourceData(crm=deals, source_ids=["crm"])
        return SourceData(source_ids=[self.source_type])
