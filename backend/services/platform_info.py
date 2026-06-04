"""Platform deployment truth for buyers, pilots, and operators."""
from __future__ import annotations

from typing import List, Literal

from backend.config import NexusConfig
from backend.integration.capabilities import list_builtin_capabilities
from backend.schemas.models import PlatformInfo

LaunchVerdict = Literal["not_ready", "demo_ready", "pilot_ready", "beta_ready", "production_ready"]
DeploymentMode = Literal["demo", "pre_live", "staging", "production"]


def deployment_mode(config: NexusConfig) -> DeploymentMode:
    if config.nexus_pre_live_mode:
        return "pre_live"
    if config.is_demo():
        return "demo"
    if config.auth_mode == "jwt_required" and config.nexus_ws_require_auth:
        return "production"
    return "staging"


def pilot_blockers(config: NexusConfig) -> List[str]:
    blockers: List[str] = []
    if config.is_demo() and not config.nexus_pre_live_mode:
        blockers.append("Running in demo mode — synthetic data only; enable NEXUS_PRE_LIVE_MODE for dress rehearsal.")
    if config.trust_client_role():
        blockers.append("Client-supplied X-Nexus-Role is trusted — disable for paid pilots (pre-live or production profile).")
    if config.auth_mode != "jwt_required":
        blockers.append("AUTH_MODE is not jwt_required — require JWT at gateway for paid pilots.")
    if not config.nexus_ws_require_auth and config.auth_mode == "jwt_required":
        blockers.append("WebSocket auth not enforced — set NEXUS_WS_REQUIRE_AUTH=true for pilots.")
    if config.jwt_secret == "change-me":
        blockers.append("JWT_SECRET is default — rotate before any external pilot.")
    if config.nexus_api_key == "demo-key":
        blockers.append("NEXUS_API_KEY is default — rotate before any external pilot.")
    if not config.plaid_configured() and not config.is_demo():
        blockers.append("No live bank connector configured — Plaid sandbox recommended for first live pilot.")
    if not config.llm_configured() and not config.uses_demo_pipeline():
        blockers.append("Live LLM not configured — pipeline requires demo/pre-live or provider keys.")
    elif config.llm_configured() and config.uses_demo_pipeline() and not config.nexus_live_llm:
        blockers.append(
            "LLM keys detected but NEXUS_LIVE_LLM=false — set NEXUS_LIVE_LLM=true for live AI narratives on demo data."
        )
    blockers.append("Per-tenant database isolation is not implemented — single shared memory layer.")
    return blockers


def launch_verdict(config: NexusConfig) -> LaunchVerdict:
    if config.uses_live_llm() and (
        config.plaid_configured() or config.alpaca_configured() or config.uses_demo_pipeline()
    ):
        if config.auth_mode == "jwt_required" and not config.trust_client_role():
            return "beta_ready"
        if config.nexus_live_llm:
            return "pilot_ready"
    if not config.is_demo() and config.llm_configured() and (
        config.plaid_configured() or config.alpaca_configured()
    ):
        if config.auth_mode == "jwt_required" and not config.trust_client_role():
            return "beta_ready"
    if config.nexus_pre_live_mode or (
        config.is_demo() and config.auth_mode in ("jwt_optional", "jwt_required")
    ):
        return "pilot_ready"
    if config.is_demo():
        return "demo_ready"
    return "not_ready"


def build_platform_info(config: NexusConfig) -> PlatformInfo:
    mode = deployment_mode(config)
    verdict = launch_verdict(config)
    caps = {
        spec["source_type"]: {
            "data_mode": spec["data_mode"],
            "live_vendor": spec.get("live_vendor"),
            "notes": spec["notes"],
        }
        for spec in list_builtin_capabilities(config)
    }
    return PlatformInfo(
        product_name="Fluf37",
        product_wedge="Pre-Release Risk Review",
        icp="Mid-market B2B CFO office ($50M–$300M revenue)",
        deployment_mode=mode,
        launch_verdict=verdict,
        uses_demo_pipeline=config.uses_demo_pipeline(),
        llm_mode=config.llm_mode(),  # type: ignore[arg-type]
        llm_provider=config.llm_provider if config.llm_configured() else None,
        auth_mode=config.auth_mode,
        trust_client_role=config.trust_client_role(),
        connector_capabilities=caps,
        pilot_blockers=pilot_blockers(config),
    )
