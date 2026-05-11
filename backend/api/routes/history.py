"""History API routes."""
from fastapi import APIRouter, Query

router = APIRouter(prefix="/api/history", tags=["history"])


@router.get("")
async def get_history(
    page: int = Query(1, ge=1),
    limit: int = Query(20, le=100),
    type: str = Query("all")
):
    return {"analyses": [], "total": 0, "page": page, "limit": limit}


@router.get("/whale-library")
async def get_whale_library(
    page: int = Query(1, ge=1),
    limit: int = Query(20, le=100),
    sort_by: str = Query("score")
):
    return {"whales": [], "total": 0, "page": page}
