"""Reverse analysis API routes."""
import json
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Query, Request

router = APIRouter(prefix="/api/reverse", tags=["reverse"])


@router.post("/start")
async def start_reverse(
    request: Request,
    address: str = Query(...),
    mode: str = Query("deep"),
    chain: str = Query("bsc"),
):
    """Create analysis record and push reverse_analysis task to Redis."""
    pg = request.app.state.pg
    redis = request.app.state.redis

    analysis_id = uuid.uuid4().hex[:16]
    now = datetime.now(timezone.utc)

    await pg.execute(
        """
        INSERT INTO analyses (id, whale_address, analysis_type, status, mode, chain, created_at)
        VALUES ($1, $2, 'reverse', 'pending', $3, $4, $5)
        """,
        analysis_id, address, mode, chain, now,
    )

    task = {
        "task_id": analysis_id,
        "task_type": "reverse_analysis",
        "payload": {"address": address, "chain": chain, "mode": mode},
        "timeout": 600,
    }
    await redis.lpush("wm:task_queue", json.dumps(task))

    return {
        "analysis_id": analysis_id,
        "address": address,
        "mode": mode,
        "chain": chain,
        "status": "pending",
    }
