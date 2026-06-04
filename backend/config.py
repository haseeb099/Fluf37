"""Nexus configuration via pydantic-settings."""
from functools import lru_cache
from typing import List, Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class NexusConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    nexus_demo_mode: bool = Field(default=True, alias="NEXUS_DEMO_MODE")
    nexus_pre_live_mode: bool = Field(default=False, alias="NEXUS_PRE_LIVE_MODE")
    nexus_trust_client_role: bool = Field(default=True, alias="NEXUS_TRUST_CLIENT_ROLE")
    nexus_api_key: str = Field(default="demo-key", alias="NEXUS_API_KEY")
    nexus_demo_seed: int = Field(default=42, alias="NEXUS_DEMO_SEED")
    nexus_live_llm: bool = Field(
        default=False,
        alias="NEXUS_LIVE_LLM",
        description="Use live LLM provider even when demo/pre-live synthetic data is active",
    )
    nexus_llm_fallback_on_error: bool = Field(
        default=True,
        alias="NEXUS_LLM_FALLBACK_ON_ERROR",
        description="When demo/pre-live pipeline is active, fall back to canned LLM output if live provider fails",
    )

    anthropic_api_key: str = Field(default="demo", alias="ANTHROPIC_API_KEY")
    openai_api_key: str = Field(default="demo", alias="OPENAI_API_KEY")
    groq_api_key: str = Field(default="demo", alias="GROQ_API_KEY")
    groq_base_url: str = Field(default="https://api.groq.com/openai/v1", alias="GROQ_BASE_URL")
    primary_model: str = "claude-3-5-sonnet-20241022"
    fallback_model: str = "gpt-4o"
    groq_model: str = Field(default="llama-3.3-70b-versatile", alias="GROQ_MODEL")
    max_tokens_per_agent: int = 2048
    agent_timeout_seconds: int = 30

    jwt_secret: str = Field(default="change-me", alias="JWT_SECRET")
    jwt_expire_minutes: int = Field(default=60, alias="JWT_EXPIRE_MINUTES")
    auth_mode: Literal["api_key_only", "jwt_optional", "jwt_required"] = Field(
        default="jwt_optional", alias="AUTH_MODE"
    )
    nexus_ws_require_auth: bool = Field(default=False, alias="NEXUS_WS_REQUIRE_AUTH")
    rate_limit_per_minute: int = Field(default=60, alias="NEXUS_RATE_LIMIT_PER_MINUTE")
    rate_limit_demo_per_minute: int = Field(default=600, alias="NEXUS_RATE_LIMIT_DEMO_PER_MINUTE")

    plaid_client_id: str = Field(default="", alias="PLAID_CLIENT_ID")
    plaid_secret: str = Field(default="", alias="PLAID_SECRET")
    plaid_env: str = Field(default="sandbox", alias="PLAID_ENV")
    alpaca_api_key: str = Field(default="", alias="ALPACA_API_KEY")
    alpaca_secret_key: str = Field(default="", alias="ALPACA_SECRET_KEY")
    alpaca_base_url: str = Field(
        default="https://paper-api.alpaca.markets", alias="ALPACA_BASE_URL"
    )
    llm_provider: Literal["anthropic", "openai", "groq"] = Field(
        default="anthropic", alias="LLM_PROVIDER"
    )

    cors_origins: str = Field(
        default="http://localhost:3000,http://127.0.0.1:3000", alias="CORS_ORIGINS"
    )

    enabled_connectors: str = Field(
        default="crm,erp,bank,trading,news", alias="NEXUS_ENABLED_CONNECTORS"
    )
    connector_sync_interval_seconds: int = 300

    vector_db_path: str = Field(default="./data/chroma", alias="VECTOR_DB_PATH")
    graph_db_path: str = Field(default="./data/graph.json", alias="GRAPH_DB_PATH")
    sqlite_path: str = Field(default="./data/nexus.db", alias="SQLITE_PATH")
    plugin_store_path: str = Field(default="./data/plugins/registered.json", alias="PLUGIN_STORE_PATH")

    evolution_cycle_days: int = 7
    min_feedback_for_update: int = 5
    max_weight_change_per_cycle: float = 0.15

    adversarial_max_iterations: int = 5
    traceback_max_results: int = 5

    ingest_hmac_secret_crm: str = Field(default="demo-crm-secret", alias="INGEST_HMAC_SECRET_CRM")
    ingest_hmac_secret_bank: str = Field(default="demo-bank-secret", alias="INGEST_HMAC_SECRET_BANK")
    ingest_hmac_secret_erp: str = Field(default="demo-erp-secret", alias="INGEST_HMAC_SECRET_ERP")

    nexus_enable_bank: bool = Field(default=False, alias="NEXUS_ENABLE_BANK")
    nexus_enable_trading: bool = Field(default=False, alias="NEXUS_ENABLE_TRADING")
    nexus_enable_crm: bool = Field(default=False, alias="NEXUS_ENABLE_CRM")
    nexus_enable_erp: bool = Field(default=False, alias="NEXUS_ENABLE_ERP")
    nexus_enable_news: bool = Field(default=False, alias="NEXUS_ENABLE_NEWS")

    def is_demo(self) -> bool:
        return self.nexus_demo_mode

    def uses_demo_pipeline(self) -> bool:
        """Deterministic synthetic data + demo LLM (demo or pre-live evaluation)."""
        return self.nexus_demo_mode or self.nexus_pre_live_mode

    def trust_client_role(self) -> bool:
        """Allow X-Nexus-Role on API-key auth. Off in pre-live and production-like modes."""
        if self.nexus_pre_live_mode:
            return False
        if not self.nexus_demo_mode:
            return False
        return self.nexus_trust_client_role

    def get_cors_origins(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    def get_enabled_connectors(self) -> List[str]:
        return [c.strip() for c in self.enabled_connectors.split(",") if c.strip()]

    def get_ingest_secret(self, source: str) -> str:
        return getattr(self, f"ingest_hmac_secret_{source}", "demo-secret")

    def get_rate_limit(self) -> str:
        relaxed = self.is_demo() or self.nexus_pre_live_mode
        limit = self.rate_limit_demo_per_minute if relaxed else self.rate_limit_per_minute
        return f"{limit}/minute"

    def plaid_configured(self) -> bool:
        return bool(self.plaid_client_id and self.plaid_secret)

    def alpaca_configured(self) -> bool:
        return bool(self.alpaca_api_key and self.alpaca_secret_key)

    def llm_configured(self) -> bool:
        if self.llm_provider == "anthropic":
            return bool(self.anthropic_api_key and self.anthropic_api_key != "demo")
        if self.llm_provider == "groq":
            return bool(self.groq_api_key and self.groq_api_key != "demo")
        return bool(self.openai_api_key and self.openai_api_key != "demo")

    def active_llm_model(self) -> str:
        if self.llm_provider == "anthropic":
            return self.primary_model
        if self.llm_provider == "groq":
            return self.groq_model
        return self.fallback_model

    def uses_live_llm(self) -> bool:
        """True when provider keys are set and live LLM is allowed for this deployment mode."""
        if not self.llm_configured():
            return False
        if self.nexus_live_llm:
            return True
        return not self.uses_demo_pipeline()

    def llm_mode(self) -> str:
        if self.uses_live_llm():
            return "live"
        if self.uses_demo_pipeline():
            return "canned"
        return "unconfigured"


@lru_cache
def get_config() -> NexusConfig:
    return NexusConfig()
