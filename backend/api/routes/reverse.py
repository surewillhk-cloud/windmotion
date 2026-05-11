"""Reverse analysis API routes."""
from fastapi import APIRouter, Query

router = APIRouter(prefix="/api/reverse", tags=["reverse"])


@router.post("/start")
async def start_reverse(
    address: str = Query(...),
    mode: str = Query("deep"),
    chain: str = Query("bsc")
):
    import uuid
    analysis_id = str(uuid.uuid4())[:8]
    return {
        "analysis_id": analysis_id,
        "address": address,
        "mode": mode,
        "chain": chain,
        "status": "pending"
    }
