from datetime import datetime
from typing import Any, Dict

from backend.connectors.base import BaseConnector
from backend.schemas.models import ConnectionStatus, SourceData, TradingPosition
from backend.utils.synthetic_data import get_demo_trading


class TradingConnector(BaseConnector):
    source_type = "trading"

    async def connect(self) -> ConnectionStatus:
        self._connected = True
        return self.get_status()

    async def disconnect(self) -> None:
        self._connected = False

    async def fetch_batch(self) -> Dict[str, Any]:
        self._last_sync = datetime.utcnow()
        if self.config.is_demo() or not self.config.nexus_enable_trading:
            return {"positions": [p.model_dump() for p in get_demo_trading()]}
        return {"positions": []}

    def normalize(self, raw: Dict[str, Any]) -> SourceData:
        positions = [TradingPosition(**p) for p in raw.get("positions", [])]
        return SourceData(trading=positions, source_ids=["trading"])
