"""Plugin marketplace and integration registration API."""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from backend.auth.deps import AuthContext, Role, get_current_tenant, require_auth, require_role
from backend.config import get_config
from backend.integration.plugin_store import PluginStore
from backend.schemas.models import PluginCatalogResponse, PluginManifest, PluginRegistrationRequest
from backend.services.plugin_catalog import build_plugin_catalog, catalog_summary, get_plugin

router = APIRouter(prefix="/api/v1/plugins", tags=["Plugins"])


def _get_store() -> PluginStore:
    return PluginStore(get_config().plugin_store_path)


@router.get("", response_model=PluginCatalogResponse)
async def list_plugins(
    category: Optional[str] = Query(None),
    installed: bool = Query(False),
    tenant: str = Depends(get_current_tenant),
    _auth: AuthContext = Depends(require_auth),
):
    from backend.main import get_connection_manager

    cfg = get_config()
    mgr = get_connection_manager(tenant)
    store = _get_store()
    plugins = build_plugin_catalog(cfg, mgr, store, tenant, category=category, installed_only=installed)
    return PluginCatalogResponse(plugins=plugins, summary=catalog_summary(plugins))


@router.get("/{plugin_id}", response_model=PluginManifest)
async def plugin_detail(
    plugin_id: str,
    tenant: str = Depends(get_current_tenant),
    _auth: AuthContext = Depends(require_auth),
):
    from backend.main import get_connection_manager

    cfg = get_config()
    mgr = get_connection_manager(tenant)
    store = _get_store()
    plugin = get_plugin(cfg, mgr, store, tenant, plugin_id)
    if not plugin:
        raise HTTPException(status_code=404, detail="Plugin not found")
    return plugin


@router.post("/register", response_model=PluginManifest)
async def register_plugin(
    body: PluginRegistrationRequest,
    tenant: str = Depends(get_current_tenant),
    _auth: AuthContext = Depends(require_auth),
    __: Role = Depends(require_role("admin")),
):
    store = _get_store()
    return store.register(tenant, body)


@router.delete("/{plugin_id}")
async def unregister_plugin(
    plugin_id: str,
    tenant: str = Depends(get_current_tenant),
    _auth: AuthContext = Depends(require_auth),
    __: Role = Depends(require_role("admin")),
):
    if not plugin_id.startswith("custom-"):
        raise HTTPException(status_code=400, detail="Only community plugins can be removed")
    store = _get_store()
    if not store.delete(tenant, plugin_id):
        raise HTTPException(status_code=404, detail="Plugin not found")
    return {"removed": plugin_id}
