"""Platform deployment truth for GTM and operator checks."""
from fastapi import APIRouter, Depends, Request

from backend.auth.deps import require_auth, require_role
from backend.config import get_config
from backend.schemas.models import PlatformInfo
from backend.services.platform_info import build_platform_info
from backend.utils.llm_client import LLMClient

router = APIRouter(prefix="/api/v1/platform", tags=["Platform"])


@router.get("/info", response_model=PlatformInfo)
async def platform_info(
    request: Request,
    _auth=Depends(require_auth),
):
    """Deployment mode, launch verdict, connector truth, and pilot blockers."""
    return build_platform_info(get_config())


@router.post("/llm-check")
async def llm_check(
    _role=Depends(require_role("admin")),
):
    """Verify live LLM provider connectivity (admin only)."""
    config = get_config()
    client = LLMClient(config)
    result = await client.verify_connectivity()
    return {
        **result,
        "uses_live_llm": config.uses_live_llm(),
        "llm_mode": config.llm_mode(),
        "demo_pipeline": config.uses_demo_pipeline(),
    }
