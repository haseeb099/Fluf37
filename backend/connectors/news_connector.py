from datetime import datetime
from typing import Any, Dict

from backend.connectors.base import BaseConnector
from backend.schemas.models import ConnectionStatus, NewsItem, SourceData
from backend.utils.synthetic_data import get_demo_news


class NewsConnector(BaseConnector):
    source_type = "news"

    async def connect(self) -> ConnectionStatus:
        self._connected = True
        return self.get_status()

    async def disconnect(self) -> None:
        self._connected = False

    async def fetch_batch(self) -> Dict[str, Any]:
        self._last_sync = datetime.utcnow()
        if self.config.uses_demo_pipeline() or not self.config.nexus_enable_news:
            return {"articles": [a.model_dump() for a in get_demo_news()]}
        return {"articles": []}

    def normalize(self, raw: Dict[str, Any]) -> SourceData:
        articles = [NewsItem(**a) for a in raw.get("articles", [])]
        return SourceData(news=articles, source_ids=["news"])
