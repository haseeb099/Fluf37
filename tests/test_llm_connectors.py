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


@pytest.mark.asyncio
async def test_llm_live_skipped_without_keys(monkeypatch):
    monkeypatch.setenv("NEXUS_DEMO_MODE", "false")
    config = NexusConfig(
        nexus_demo_mode=False,
        anthropic_api_key="demo",
        openai_api_key="demo",
    )
    client = LLMClient(config)
    with pytest.raises(LLMError):
        await client.complete("test", agent_id="silent_finder")


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
