from datetime import datetime
from typing import Any, Dict

import structlog

from backend.connectors.base import BaseConnector
from backend.connectors.live.alpaca_client import AlpacaClient
from backend.schemas.models import ConnectionStatus, SourceData, TradingPosition
from backend.utils.synthetic_data import get_demo_trading

logger = structlog.get_logger()


class TradingConnector(BaseConnector):
    source_type = "trading"
    live_vendor = "alpaca"

    async def connect(self) -> ConnectionStatus:
        self._connected = True
        return self.get_status()

    async def disconnect(self) -> None:
        self._connected = False

    async def fetch_batch(self) -> Dict[str, Any]:
        self._last_sync = datetime.utcnow()
        if self.config.uses_demo_pipeline() or not self.config.nexus_enable_trading:
            return {"positions": [p.model_dump() for p in get_demo_trading()]}
        if self.config.alpaca_configured():
            client = AlpacaClient(
                self.config.alpaca_api_key,
                self.config.alpaca_secret_key,
                self.config.alpaca_base_url,
            )
            raw_positions = await client.fetch_positions()
            positions = [
                TradingPosition(
                    ticker=str(p.get("symbol", "UNKNOWN")),
                    qty=float(p.get("qty", p.get("quantity", 0))),
                    current_price=float(p.get("current_price", p.get("market_value", 0))),
                )
                for p in raw_positions
            ]
            return {"positions": [p.model_dump() for p in positions]}
        logger.warning("trading_live_not_configured")
        return {"positions": []}

    def normalize(self, raw: Dict[str, Any]) -> SourceData:
        positions = [TradingPosition(**p) for p in raw.get("positions", [])]
        return SourceData(trading=positions, source_ids=["trading"])
