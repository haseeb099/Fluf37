"""Append-only tamper-evident audit log."""
import hashlib
import json
from pathlib import Path
from typing import Literal

from backend.schemas.models import AuditEntry, AuditVerification

AUDIT_PATH = Path("data/audit.jsonl")


class AuditLog:
    def __init__(self, path: Path = AUDIT_PATH):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _last_hash(self) -> str:
        if not self.path.exists():
            return "genesis"
        last_line = ""
        with open(self.path, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    last_line = line
        if not last_line:
            return "genesis"
        return json.loads(last_line).get("hash", "genesis")

    def write(self, entry: AuditEntry) -> str:
        prev_hash = self._last_hash()
        entry_json = entry.model_dump_json()
        entry_hash = hashlib.sha256((entry_json + prev_hash).encode()).hexdigest()
        record = {**entry.model_dump(mode="json"), "hash": entry_hash, "prev_hash": prev_hash}
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
        return entry_hash

    def verify(self) -> AuditVerification:
        if not self.path.exists():
            return AuditVerification(valid=True, entries_checked=0)
        prev = "genesis"
        count = 0
        with open(self.path, encoding="utf-8") as f:
            for i, line in enumerate(f):
                if not line.strip():
                    continue
                record = json.loads(line)
                entry_json = json.dumps(
                    {k: v for k, v in record.items() if k not in ("hash", "prev_hash")},
                    default=str,
                )
                expected = hashlib.sha256((entry_json + prev).encode()).hexdigest()
                if record.get("hash") != expected:
                    return AuditVerification(valid=False, entries_checked=count, first_invalid_index=i)
                prev = record["hash"]
                count += 1
        return AuditVerification(valid=True, entries_checked=count)

    def export(self, fmt: Literal["json"] = "json") -> bytes:
        if not self.path.exists():
            return b"[]"
        lines = self.path.read_text(encoding="utf-8").strip().split("\n")
        return ("[" + ",".join(lines) + "]").encode()
