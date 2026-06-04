from datetime import datetime
from typing import Any, Dict

from backend.connectors.base import BaseConnector
from backend.schemas.models import BankTransaction, ConnectionStatus, SourceData
from backend.utils.synthetic_data import get_demo_bank


class BankConnector(BaseConnector):
    source_type = "bank"
    supports_webhook = True

    async def connect(self) -> ConnectionStatus:
        self._connected = True
        return self.get_status()

    async def disconnect(self) -> None:
        self._connected = False

    async def fetch_batch(self) -> Dict[str, Any]:
        self._last_sync = datetime.utcnow()
        if self.config.is_demo() or not self.config.nexus_enable_bank:
            return {"transactions": [t.model_dump() for t in get_demo_bank()]}
        return {"transactions": []}

    def normalize(self, raw: Dict[str, Any]) -> SourceData:
        txs = [BankTransaction(**t) for t in raw.get("transactions", [])]
        return SourceData(bank=txs, source_ids=["bank"])
