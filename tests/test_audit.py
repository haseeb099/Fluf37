import json
from pathlib import Path

import pytest
from backend.schemas.models import AuditEntry
from backend.utils.audit_log import AuditLog


@pytest.fixture
def audit_path(tmp_path: Path) -> Path:
    return tmp_path / "audit.jsonl"


def test_audit_write_and_verify(audit_path: Path):
    log = AuditLog(path=audit_path)
    for i in range(3):
        log.write(
            AuditEntry(
                agent_id=f"agent_{i}",
                action="test_action",
                payload_preview=f"payload-{i}",
                tokens=10 + i,
            )
        )
    result = log.verify()
    assert result.valid is True
    assert result.entries_checked == 3


def test_audit_verify_detects_tamper(audit_path: Path):
    log = AuditLog(path=audit_path)
    log.write(AuditEntry(agent_id="a1", action="run", payload_preview="ok"))
    log.write(AuditEntry(agent_id="a2", action="run", payload_preview="ok"))
    lines = audit_path.read_text(encoding="utf-8").strip().split("\n")
    record = json.loads(lines[1])
    record["payload_preview"] = "tampered"
    lines[1] = json.dumps(record)
    audit_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    result = log.verify()
    assert result.valid is False
    assert result.first_invalid_index == 1
