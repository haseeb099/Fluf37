from fastapi import APIRouter, Depends, Query

from backend.auth.deps import AuthContext, require_auth

router = APIRouter(prefix="/api/v1/memory", tags=["Memory"])


@router.get("/search")
async def search_memory(q: str = Query(...), n: int = 5, _auth: AuthContext = Depends(require_auth)):
    from backend.main import get_memory
    results = await get_memory().search(q, n)
    return [r.model_dump() for r in results]


@router.get("/graph")
async def get_graph(_auth: AuthContext = Depends(require_auth)):
    from backend.main import get_memory
    g = get_memory().get_graph()
    return g.serialize()


@router.get("/stats")
async def memory_stats(_auth: AuthContext = Depends(require_auth)):
    from backend.main import get_memory
    return (await get_memory().get_stats()).model_dump()
