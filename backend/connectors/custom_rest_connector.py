from datetime import datetime
from typing import Any, Dict

from backend.connectors.base import BaseConnector
from backend.schemas.models import ConnectionStatus, SourceData


class CustomRESTConnector(BaseConnector):
    source_type = "custom"

    async def connect(self) -> ConnectionStatus:
        self._connected = True
        return self.get_status()

    async def disconnect(self) -> None:
        self._connected = False

    async def fetch_batch(self) -> Dict[str, Any]:
        self._last_sync = datetime.utcnow()
        return {}

    def normalize(self, raw: Dict[str, Any]) -> SourceData:
        return SourceData(source_ids=["custom"])
