import pytest
from backend.config import get_config
from backend.integration.connection_manager import ConnectionManager


@pytest.mark.asyncio
async def test_sync_all_demo():
    get_config.cache_clear()
    config = get_config()
    config.nexus_demo_mode = True
    mgr = ConnectionManager(config)
    output = await mgr.sync_all(demo=True)
    assert len(output.connections) >= 5
    assert len(output.source_data.crm) >= 1
    assert len(output.source_data.bank) >= 1
    assert len(output.source_data.erp.vendors) >= 1
