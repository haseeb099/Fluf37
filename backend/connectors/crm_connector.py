from datetime import datetime
from typing import Any, Dict

from backend.connectors.base import BaseConnector
from backend.schemas.models import ConnectionStatus, CRMDeal, EquityHolder, SourceData
from backend.utils.synthetic_data import get_demo_crm


class CRMConnector(BaseConnector):
    source_type = "crm"

    async def connect(self) -> ConnectionStatus:
        self._connected = True
        return self.get_status()

    async def disconnect(self) -> None:
        self._connected = False

    async def fetch_batch(self) -> Dict[str, Any]:
        self._last_sync = datetime.utcnow()
        if self.config.uses_demo_pipeline() or not self.config.nexus_enable_crm:
            return {"deals": [d.model_dump() for d in get_demo_crm()]}
        return {"deals": []}

    def normalize(self, raw: Dict[str, Any]) -> SourceData:
        deals = []
        for d in raw.get("deals", []):
            holders = [EquityHolder(**h) for h in d.get("equity_holders", [])]
            deals.append(CRMDeal(**{**d, "equity_holders": holders}))
        return SourceData(crm=deals, source_ids=["crm"])
