import hashlib
import hmac
import json

from fastapi import APIRouter, Depends, Header, HTTPException, Request

from backend.auth.deps import AuthContext, require_auth
from backend.config import get_config
from backend.rate_limit import limiter
from backend.schemas.models import SourceType

router = APIRouter(prefix="/ingest", tags=["Ingest"])


def _verify_hmac(body: bytes, signature: str, secret: str) -> bool:
    expected = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature or "")


@router.post("/{source}")
@limiter.limit("30/minute")
async def ingest_webhook(
    source: SourceType,
    request: Request,
    _auth: AuthContext = Depends(require_auth),
    x_nexus_signature: str = Header(None, alias="X-Nexus-Signature"),
    x_nexus_tenant_id: str = Header("default", alias="X-Nexus-Tenant-Id"),
):
    config = get_config()
    body = await request.body()
    secret = config.get_ingest_secret(source)
    if not config.is_demo() and not _verify_hmac(body, x_nexus_signature or "", secret):
        raise HTTPException(status_code=401, detail="Invalid signature")
    payload = json.loads(body) if body else {}
    from backend.main import get_connection_manager

    mgr = get_connection_manager(x_nexus_tenant_id)
    partial = await mgr.ingest_webhook(source, payload)
    return {
        "ingested": source,
        "records": len(partial.bank) + len(partial.crm) + len(partial.trading),
    }
