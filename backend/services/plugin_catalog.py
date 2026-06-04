"""Unified plugin catalog: official connectors + community registrations."""
from __future__ import annotations

from typing import List, Optional

from backend.config import NexusConfig
from backend.integration.capabilities import build_capability
from backend.integration.connection_manager import ConnectionManager
from backend.integration.plugin_store import PluginStore
from backend.integration.registry import BUILTIN, ConnectorRegistry
from backend.schemas.models import PluginCatalogSummary, PluginManifest, SourceType

_OFFICIAL: List[dict] = [
    {
        "id": "nexus-crm",
        "name": "CRM Intelligence",
        "description": "Pipeline deals, contacts, and payment terms from Salesforce or HubSpot.",
        "category": "revenue",
        "integration_type": "builtin",
        "tier": "official",
        "vendor": "Fluf37",
        "version": "1.0.0",
        "source_type": "crm",
        "supports_webhook": True,
        "live_vendor": "salesforce",
        "icon": "users",
        "setup_steps": [
            "Enable NEXUS_ENABLE_CRM in environment",
            "Configure Salesforce or HubSpot credentials",
            "Click Connect, then Sync to ingest deals",
        ],
        "required_env": ["NEXUS_ENABLE_CRM", "SALESFORCE_CLIENT_ID"],
    },
    {
        "id": "nexus-erp",
        "name": "ERP & GL",
        "description": "Vendor spend, GL snapshots, and payment flows from NetSuite or QuickBooks.",
        "category": "finance",
        "integration_type": "builtin",
        "tier": "official",
        "vendor": "Fluf37",
        "version": "1.0.0",
        "source_type": "erp",
        "supports_webhook": True,
        "live_vendor": "netsuite",
        "icon": "ledger",
        "setup_steps": [
            "Enable NEXUS_ENABLE_ERP",
            "Configure ERP credentials or webhook ingest",
            "Sync to merge vendor concentration signals",
        ],
        "required_env": ["NEXUS_ENABLE_ERP"],
    },
    {
        "id": "nexus-bank",
        "name": "Banking & Cash",
        "description": "Operating accounts, transactions, and 30-day cash forecasts via Plaid.",
        "category": "banking",
        "integration_type": "builtin",
        "tier": "official",
        "vendor": "Fluf37",
        "version": "1.0.0",
        "source_type": "bank",
        "supports_webhook": True,
        "live_vendor": "plaid",
        "icon": "landmark",
        "setup_steps": [
            "Enable NEXUS_ENABLE_BANK",
            "Add PLAID_CLIENT_ID and PLAID_SECRET",
            "Connect and sync for live or sandbox transactions",
        ],
        "required_env": ["NEXUS_ENABLE_BANK", "PLAID_CLIENT_ID", "PLAID_SECRET"],
    },
    {
        "id": "nexus-trading",
        "name": "Trading Desk",
        "description": "Positions, order book imbalance, and technical signals from Alpaca.",
        "category": "markets",
        "integration_type": "builtin",
        "tier": "official",
        "vendor": "Fluf37",
        "version": "1.0.0",
        "source_type": "trading",
        "supports_webhook": False,
        "live_vendor": "alpaca",
        "icon": "trending",
        "setup_steps": [
            "Enable NEXUS_ENABLE_TRADING",
            "Configure Alpaca paper or live keys",
            "Sync before running risk review",
        ],
        "required_env": ["NEXUS_ENABLE_TRADING", "ALPACA_API_KEY"],
    },
    {
        "id": "nexus-news",
        "name": "News & Sentiment",
        "description": "Headlines and entity sentiment for counterparty and market context.",
        "category": "intelligence",
        "integration_type": "builtin",
        "tier": "official",
        "vendor": "Fluf37",
        "version": "1.0.0",
        "source_type": "news",
        "supports_webhook": False,
        "live_vendor": "newsapi",
        "icon": "newspaper",
        "setup_steps": [
            "Enable NEXUS_ENABLE_NEWS",
            "Configure NewsAPI key when live path ships",
            "Sync to enrich blind-spot detection",
        ],
        "required_env": ["NEXUS_ENABLE_NEWS"],
    },
    {
        "id": "nexus-custom-rest",
        "name": "Custom REST",
        "description": "Bring your own REST endpoint mapped to Nexus SourceData.",
        "category": "custom",
        "integration_type": "rest",
        "tier": "official",
        "vendor": "Fluf37",
        "version": "1.0.0",
        "source_type": "custom",
        "supports_webhook": False,
        "icon": "code",
        "setup_steps": [
            "Implement a REST adapter returning SourceData fields",
            "Register via Add Integration or CONNECTOR_PLUGINS",
            "Connect and sync as custom source",
        ],
        "required_env": [],
    },
    {
        "id": "nexus-webhook",
        "name": "Webhook Ingest",
        "description": "Push JSON from any system with HMAC-signed POST /ingest/{source}.",
        "category": "custom",
        "integration_type": "webhook",
        "tier": "official",
        "vendor": "Fluf37",
        "version": "1.0.0",
        "source_type": "webhook",
        "supports_webhook": True,
        "icon": "webhook",
        "setup_steps": [
            "Choose a source slug (e.g. my_erp)",
            "Set INGEST_HMAC_SECRET_* in environment",
            "POST signed payloads to /ingest/{source}",
        ],
        "required_env": ["INGEST_HMAC_SECRET_CRM"],
    },
]


def _attach_status(
    manifest: PluginManifest,
    config: NexusConfig,
    statuses: dict,
) -> PluginManifest:
    st = manifest.source_type
    if st and st in statuses:
        s = statuses[st]
        manifest.connection_state = s.state
        manifest.data_mode = s.data_mode
        manifest.installed = s.state in ("connected", "degraded")
    elif manifest.integration_type in ("webhook", "rest") and manifest.tier == "community":
        manifest.installed = True
    elif st:
        cls = BUILTIN.get(st)  # type: ignore[arg-type]
        if cls:
            cap = build_capability(
                config,
                st,  # type: ignore[arg-type]
                supports_webhook=getattr(cls, "supports_webhook", False),
                live_vendor=getattr(cls, "live_vendor", None),
            )
            manifest.data_mode = cap["data_mode"]
    return manifest


def build_plugin_catalog(
    config: NexusConfig,
    connection_manager: ConnectionManager,
    store: PluginStore,
    tenant_id: str,
    *,
    category: Optional[str] = None,
    installed_only: bool = False,
) -> List[PluginManifest]:
    statuses = {s.source_type: s for s in connection_manager.get_all_status()}
    plugins: List[PluginManifest] = []

    for row in _OFFICIAL:
        manifest = PluginManifest.model_validate(row)
        plugins.append(_attach_status(manifest, config, statuses))

    for custom in store.list_for_tenant(tenant_id):
        plugins.append(_attach_status(custom, config, statuses))

    if category:
        plugins = [p for p in plugins if p.category == category]
    if installed_only:
        plugins = [p for p in plugins if p.installed]
    return plugins


def get_plugin(
    config: NexusConfig,
    connection_manager: ConnectionManager,
    store: PluginStore,
    tenant_id: str,
    plugin_id: str,
) -> Optional[PluginManifest]:
    for p in build_plugin_catalog(config, connection_manager, store, tenant_id):
        if p.id == plugin_id:
            return p
    return None


def catalog_summary(plugins: List[PluginManifest]) -> PluginCatalogSummary:
    return PluginCatalogSummary(
        total=len(plugins),
        installed=sum(1 for p in plugins if p.installed),
        official=sum(1 for p in plugins if p.tier == "official"),
        community=sum(1 for p in plugins if p.tier == "community"),
        categories=sorted({p.category for p in plugins}),
    )


def registry_types(config: NexusConfig) -> List[str]:
    return ConnectorRegistry(config).list_types()
