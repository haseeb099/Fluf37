import hashlib
import hmac
import json

from fastapi import APIRouter, Header, HTTPException, Request

from backend.config import get_config
from backend.schemas.models import SourceType

router = APIRouter(prefix="/ingest", tags=["Ingest"])


def _verify_hmac(body: bytes, signature: str, secret: str) -> bool:
    expected = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature or "")


@router.post("/{source}")
async def ingest_webhook(
    source: SourceType,
    request: Request,
    x_nexus_signature: str = Header(None, alias="X-Nexus-Signature"),
    x_nexus_tenant_id: str = Header("default", alias="X-Nexus-Tenant-Id"),
):
    config = get_config()
    body = await request.body()
    secret = config.get_ingest_secret(source)
    if not config.is_demo() and not _verify_hmac(body, x_nexus_signature or "", secret):
        raise HTTPException(status_code=401, detail="Invalid signature")
    payload = json.loads(body) if body else {}
    from backend.connectors.webhook_connector import WebhookConnector
    from backend.main import get_connection_manager
    conn = WebhookConnector(config, x_nexus_tenant_id, source_type=source)
    conn.ingest(payload)
    partial = conn.normalize(payload)
    return {"ingested": source, "records": len(partial.bank) + len(partial.crm)}
