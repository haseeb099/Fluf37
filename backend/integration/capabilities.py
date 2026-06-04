"""Connector capability descriptors (truthful live vs demo vs stub)."""
from typing import List, Optional, TypedDict

from backend.config import NexusConfig
from backend.schemas.models import DataMode, SourceType


class ConnectorCapability(TypedDict):
    source_type: str
    supports_webhook: bool
    live_vendor: Optional[str]
    data_mode: DataMode
    enabled_flag: str
    notes: str


def _enable_attr(source: str) -> str:
    return f"nexus_enable_{source}"


def peek_data_mode(config: NexusConfig, source_type: SourceType, live_vendor: Optional[str] = None) -> DataMode:
    if config.uses_demo_pipeline():
        return "demo"
    if not getattr(config, _enable_attr(source_type), False):
        return "stub"
    if source_type == "bank" and not config.plaid_configured():
        return "stub"
    if source_type == "trading" and not config.alpaca_configured():
        return "stub"
    if source_type in ("crm", "erp", "news"):
        return "empty"
    if live_vendor:
        return "live"
    return "empty"


def capability_notes(mode: DataMode, source: str, vendor: Optional[str]) -> str:
    if mode == "demo":
        return "Synthetic demo JSON via uses_demo_pipeline()"
    if mode == "stub":
        if vendor:
            return f"Enable {_enable_attr(source)} and configure {vendor} credentials"
        return f"Enable {_enable_attr(source)} for live fetch (vendor integration not shipped)"
    if mode == "empty":
        return "Live flag on; vendor API returns empty until integration ships"
    if mode == "live":
        return f"Live {vendor or source} fetch enabled"
    return "Disabled"


def build_capability(
    config: NexusConfig,
    source_type: SourceType,
    supports_webhook: bool = False,
    live_vendor: Optional[str] = None,
) -> ConnectorCapability:
    mode = peek_data_mode(config, source_type, live_vendor)
    return ConnectorCapability(
        source_type=source_type,
        supports_webhook=supports_webhook,
        live_vendor=live_vendor,
        data_mode=mode,
        enabled_flag=_enable_attr(source_type),
        notes=capability_notes(mode, source_type, live_vendor),
    )


def list_builtin_capabilities(config: NexusConfig) -> List[ConnectorCapability]:
    return [
        build_capability(config, "crm"),
        build_capability(config, "erp"),
        build_capability(config, "bank", live_vendor="plaid"),
        build_capability(config, "trading", live_vendor="alpaca"),
        build_capability(config, "news"),
        build_capability(config, "custom"),
    ]
