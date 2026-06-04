import json
from pathlib import Path

import pytest
from backend.agents.orchestrator import NexusOrchestrator
from backend.config import NexusConfig
from backend.integration.connection_manager import ConnectionManager
from backend.memory.layer import MemoryLayer
from backend.utils.audit_log import AuditLog
from backend.utils.llm_client import LLMClient


@pytest.mark.asyncio
async def test_pipeline_writes_audit_chain(tmp_path: Path, monkeypatch):
    audit_path = tmp_path / "audit.jsonl"

    def _audit_factory():
        return AuditLog(path=audit_path)

    monkeypatch.setattr("backend.utils.pipeline_trace.AuditLog", _audit_factory)
    config = NexusConfig(nexus_demo_mode=True)
    memory = MemoryLayer(config)
    await memory.initialize_demo()
    mgr = ConnectionManager(config)
    orch = NexusOrchestrator(config, memory, LLMClient(config), mgr)

    async for _ in orch.run_pipeline("demo", tenant_id="t1"):
        pass

    log = AuditLog(path=audit_path)
    result = log.verify()
    assert result.valid
    assert result.entries_checked >= 8
    lines = audit_path.read_text(encoding="utf-8").strip().split("\n")
    actions = [json.loads(line)["action"] for line in lines]
    assert "pipeline_start" in actions
    assert "pipeline_complete" in actions
    assert "agent_complete" in actions
