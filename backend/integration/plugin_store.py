"""Persist tenant-scoped custom integration plugins."""
from __future__ import annotations

import json
from pathlib import Path
from typing import List
from uuid import uuid4

from backend.schemas.models import PluginManifest, PluginRegistrationRequest


class PluginStore:
    def __init__(self, path: str = "./data/plugins/registered.json"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._write([])

    def _read(self) -> List[dict]:
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return []

    def _write(self, rows: List[dict]) -> None:
        self.path.write_text(json.dumps(rows, indent=2), encoding="utf-8")

    def list_for_tenant(self, tenant_id: str) -> List[PluginManifest]:
        return [
            PluginManifest.model_validate(row)
            for row in self._read()
            if row.get("tenant_id") == tenant_id
        ]

    def register(self, tenant_id: str, req: PluginRegistrationRequest) -> PluginManifest:
        plugin_id = f"custom-{uuid4().hex[:10]}"
        source = req.webhook_source or plugin_id.replace("-", "_")
        setup = [
            f"Register webhook payloads to POST /ingest/{source}",
            "Include header X-Nexus-Tenant-Id with your tenant id",
            "Sign body with HMAC-SHA256 using your ingest secret",
        ]
        if req.integration_type == "rest":
            setup = [
                "Configure REST endpoint URL in your integration service",
                "Map response fields to Nexus SourceData schema",
                "Enable sync via POST /api/v1/connect/custom/sync",
            ]
        manifest = PluginManifest(
            id=plugin_id,
            name=req.name,
            description=req.description,
            category=req.category,
            integration_type=req.integration_type,
            tier="community",
            vendor=req.vendor,
            source_type=source if req.integration_type == "webhook" else "custom",
            supports_webhook=req.integration_type == "webhook",
            docs_url=req.docs_url,
            setup_steps=setup,
            installed=True,
        )
        rows = self._read()
        rows.append({**manifest.model_dump(), "tenant_id": tenant_id})
        self._write(rows)
        return manifest

    def delete(self, tenant_id: str, plugin_id: str) -> bool:
        rows = self._read()
        kept = [r for r in rows if not (r.get("tenant_id") == tenant_id and r.get("id") == plugin_id)]
        if len(kept) == len(rows):
            return False
        self._write(kept)
        return True

    def get(self, tenant_id: str, plugin_id: str) -> PluginManifest | None:
        for row in self._read():
            if row.get("tenant_id") == tenant_id and row.get("id") == plugin_id:
                return PluginManifest.model_validate(row)
        return None
