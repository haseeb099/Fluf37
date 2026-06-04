from backend.config import NexusConfig
from backend.integration.capabilities import peek_data_mode
from backend.integration.registry import ConnectorRegistry


def test_demo_mode_capabilities():
    config = NexusConfig(nexus_demo_mode=True)
    caps = ConnectorRegistry(config).describe_all()
    assert all(c["data_mode"] == "demo" for c in caps if c["source_type"] in ("crm", "bank"))


def test_pre_live_crm_empty_not_demo():
    config = NexusConfig(nexus_demo_mode=False, nexus_pre_live_mode=True, nexus_enable_crm=True)
    assert config.uses_demo_pipeline()
    assert peek_data_mode(config, "crm") == "demo"


def test_live_bank_stub_without_credentials():
    config = NexusConfig.model_construct(
        nexus_demo_mode=False,
        nexus_pre_live_mode=False,
        nexus_enable_bank=True,
        plaid_client_id="",
        plaid_secret="",
    )
    assert peek_data_mode(config, "bank", "plaid") == "stub"
