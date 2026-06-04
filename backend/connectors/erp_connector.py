from datetime import datetime
from typing import Any, Dict

from backend.connectors.base import BaseConnector
from backend.schemas.models import (
    ConnectionStatus,
    ERPRecord,
    ERPVendor,
    GLSnapshot,
    SourceData,
    VendorPayment,
)
from backend.utils.synthetic_data import get_demo_erp


class ERPConnector(BaseConnector):
    source_type = "erp"

    async def connect(self) -> ConnectionStatus:
        self._connected = True
        return self.get_status()

    async def disconnect(self) -> None:
        self._connected = False

    async def fetch_batch(self) -> Dict[str, Any]:
        self._last_sync = datetime.utcnow()
        if self.config.uses_demo_pipeline() or not self.config.nexus_enable_erp:
            erp = get_demo_erp()
            return erp.model_dump()
        return {}

    def normalize(self, raw: Dict[str, Any]) -> SourceData:
        erp = ERPRecord(
            vendors=[ERPVendor(**v) for v in raw.get("vendors", [])],
            gl_snapshots=[GLSnapshot(**g) for g in raw.get("gl_snapshots", [])],
            vendor_payments=[VendorPayment(**p) for p in raw.get("vendor_payments", [])],
        )
        return SourceData(erp=erp, source_ids=["erp"])
