"""Per-tenant credential storage stub."""
from typing import Any, Dict, Optional


class CredentialStore:
    def __init__(self):
        self._store: Dict[str, Dict[str, Any]] = {}

    def set(self, tenant_id: str, source_type: str, credentials: Dict[str, Any]) -> None:
        self._store.setdefault(tenant_id, {})[source_type] = credentials

    def get(self, tenant_id: str, source_type: str) -> Optional[Dict[str, Any]]:
        return self._store.get(tenant_id, {}).get(source_type)

    def delete(self, tenant_id: str, source_type: str) -> None:
        if tenant_id in self._store and source_type in self._store[tenant_id]:
            del self._store[tenant_id][source_type]
