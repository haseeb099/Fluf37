"""Connector registry."""
from typing import Dict, List, Type

from backend.config import NexusConfig
from backend.connectors.bank_connector import BankConnector
from backend.connectors.base import BaseConnector
from backend.connectors.crm_connector import CRMConnector
from backend.connectors.custom_rest_connector import CustomRESTConnector
from backend.connectors.erp_connector import ERPConnector
from backend.connectors.news_connector import NewsConnector
from backend.connectors.trading_connector import TradingConnector
from backend.integration.capabilities import build_capability, list_builtin_capabilities
from backend.schemas.models import SourceType

BUILTIN: Dict[SourceType, Type[BaseConnector]] = {
    "crm": CRMConnector,
    "erp": ERPConnector,
    "bank": BankConnector,
    "trading": TradingConnector,
    "news": NewsConnector,
    "custom": CustomRESTConnector,
}


class ConnectorRegistry:
    def __init__(self, config: NexusConfig):
        self.config = config
        self._types = dict(BUILTIN)

    def list_types(self) -> List[str]:
        return list(self._types.keys())

    def create(self, source_type: SourceType, tenant_id: str = "default") -> BaseConnector:
        cls = self._types.get(source_type)
        if not cls:
            raise ValueError(f"Unknown connector: {source_type}")
        return cls(self.config, tenant_id)

    def describe(self, source_type: SourceType) -> dict:
        cls = self._types.get(source_type)
        if not cls:
            raise ValueError(f"Unknown connector: {source_type}")
        cap = build_capability(
            self.config,
            source_type,
            supports_webhook=getattr(cls, "supports_webhook", False),
            live_vendor=getattr(cls, "live_vendor", None),
        )
        return cap

    def describe_all(self) -> list:
        return list_builtin_capabilities(self.config)
