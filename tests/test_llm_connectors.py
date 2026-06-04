import pytest
from backend.config import NexusConfig
from backend.connectors.bank_connector import BankConnector
from backend.connectors.trading_connector import TradingConnector
from backend.utils.errors import LLMError
from backend.utils.llm_client import LLMClient


@pytest.mark.asyncio
async def test_llm_demo_path_unchanged():
    client = LLMClient(NexusConfig(nexus_demo_mode=True))
    text = await client.complete("test", agent_id="silent_finder")
    assert "cross-source" in text.lower() or len(text) > 0


def test_uses_live_llm_groq():
    cfg = NexusConfig.model_construct(
        nexus_demo_mode=True,
        nexus_live_llm=True,
        groq_api_key="gsk-test-key",
        llm_provider="groq",
    )
    assert cfg.llm_configured()
    assert cfg.uses_live_llm()
    assert cfg.active_llm_model() == cfg.groq_model


def test_uses_live_llm_hybrid():
    cfg = NexusConfig.model_construct(
        nexus_demo_mode=True,
        nexus_live_llm=True,
        anthropic_api_key="sk-test-key",
        llm_provider="anthropic",
    )
    assert cfg.llm_configured()
    assert cfg.uses_live_llm()
    assert cfg.llm_mode() == "live"


def test_llm_mode_canned_in_demo():
    cfg = NexusConfig.model_construct(
        nexus_demo_mode=True,
        nexus_live_llm=False,
        anthropic_api_key="demo",
    )
    assert cfg.llm_mode() == "canned"


def test_llm_mode_unconfigured_production():
    cfg = NexusConfig.model_construct(
        nexus_demo_mode=False,
        nexus_pre_live_mode=False,
        anthropic_api_key="demo",
    )
    assert cfg.llm_mode() == "unconfigured"


@pytest.mark.asyncio
async def test_llm_live_skipped_without_keys():
    config = NexusConfig.model_construct(
        nexus_demo_mode=False,
        nexus_pre_live_mode=False,
        nexus_live_llm=False,
        anthropic_api_key="demo",
        openai_api_key="demo",
    )
    client = LLMClient(config)
    with pytest.raises(LLMError):
        await client.complete("test", agent_id="silent_finder")


@pytest.mark.asyncio
async def test_llm_fallback_on_rate_limit(monkeypatch):
    config = NexusConfig.model_construct(
        nexus_demo_mode=True,
        nexus_live_llm=True,
        nexus_llm_fallback_on_error=True,
        groq_api_key="gsk-test",
        llm_provider="groq",
    )
    client = LLMClient(config)

    async def _fail(*args, **kwargs):
        raise RuntimeError(
            "Error code: 429 - rate_limit_exceeded: tokens per day limit reached"
        )
        yield  # pragma: no cover

    monkeypatch.setattr(client, "_stream_openai_compatible", _fail)
    text = await client.complete("test", agent_id="silent_finder")
    assert "cross-source" in text.lower() or len(text) > 0


@pytest.mark.asyncio
async def test_bank_connector_demo():
    conn = BankConnector(NexusConfig(nexus_demo_mode=True), "default")
    raw = await conn.fetch_batch()
    assert len(raw["transactions"]) > 0


@pytest.mark.asyncio
async def test_bank_live_empty_without_plaid():
    config = NexusConfig.model_construct(
        nexus_demo_mode=False,
        nexus_enable_bank=True,
        plaid_client_id="",
        plaid_secret="",
    )
    conn = BankConnector(config, "default")
    raw = await conn.fetch_batch()
    assert raw["transactions"] == []


@pytest.mark.asyncio
async def test_trading_live_empty_without_alpaca():
    config = NexusConfig.model_construct(
        nexus_demo_mode=False,
        nexus_enable_trading=True,
        alpaca_api_key="",
        alpaca_secret_key="",
    )
    conn = TradingConnector(config, "default")
    raw = await conn.fetch_batch()
    assert raw["positions"] == []
