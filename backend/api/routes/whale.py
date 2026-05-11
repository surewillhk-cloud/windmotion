"""Whale API routes."""
import json
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Query, Request
from typing import Optional

router = APIRouter(prefix="/api/whales", tags=["whales"])


@router.get("/feed")
async def get_whale_feed(
    request: Request,
    chain: str = Query("bsc"),
    min_value: float = Query(100000),
    limit: int = Query(50, le=200),
    page: int = Query(1, ge=1),
):
    """Get real-time whale transaction feed from PostgreSQL."""
    pg = request.app.state.pg
    offset = (page - 1) * limit

    rows = await pg.fetch(
        """
        SELECT address, chain, total_profit_usd, win_rate, roi,
               trade_count, token_count, score, labels, strategy_patterns,
               first_seen, last_active, metadata
        FROM whales
        WHERE chain = $1 AND score > 0
        ORDER BY score DESC
        LIMIT $2 OFFSET $3
        """,
        chain, limit, offset,
    )

    total_row = await pg.fetchrow(
        "SELECT COUNT(*) AS cnt FROM whales WHERE chain = $1 AND score > 0",
        chain,
    )
    total = total_row["cnt"] if total_row else 0

    return {"feed": rows, "total": total, "chain": chain, "min_value": min_value, "page": page}


@router.get("/{address}")
async def get_whale_detail(address: str, request: Request):
    """Get whale address details from PostgreSQL."""
    pg = request.app.state.pg
    whale = await pg.fetchrow(
        """
        SELECT address, chain, total_profit_usd, win_rate, roi,
               trade_count, token_count, score, labels, strategy_patterns,
               first_seen, last_active, metadata
        FROM whales
        WHERE address = $1
        """,
        address,
    )
    if not whale:
        raise HTTPException(404, "Whale not found")
    return whale


@router.post("/{address}/analyze")
async def start_reverse_analysis(address: str, request: Request, mode: str = Query("deep")):
    """Start reverse analysis for a whale address."""
    pg = request.app.state.pg
    redis = request.app.state.redis

    analysis_id = uuid.uuid4().hex[:16]
    now = datetime.now(timezone.utc)

    await pg.execute(
        """
        INSERT INTO analyses (id, whale_address, analysis_type, status, mode, chain, created_at)
        VALUES ($1, $2, 'reverse', 'pending', $3, 'bsc', $4)
        """,
        analysis_id, address, mode, now,
    )

    task = {
        "task_id": analysis_id,
        "task_type": "reverse_analysis",
        "payload": {"address": address, "chain": "bsc", "mode": mode},
        "timeout": 600,
    }
    await redis.lpush("wm:task_queue", json.dumps(task))

    return {
        "analysis_id": analysis_id,
        "address": address,
        "mode": mode,
        "status": "pending",
        "message": "Analysis started",
    }


@router.post("/{address}/infer")
async def start_forward_inference(address: str, request: Request):
    """Start forward inference for a whale address."""
    pg = request.app.state.pg
    redis = request.app.state.redis

    analysis_id = uuid.uuid4().hex[:16]
    now = datetime.now(timezone.utc)

    await pg.execute(
        """
        INSERT INTO analyses (id, whale_address, analysis_type, status, mode, chain, created_at)
        VALUES ($1, $2, 'forward', 'pending', 'deep', 'bsc', $3)
        """,
        analysis_id, address, now,
    )

    task = {
        "task_id": analysis_id,
        "task_type": "forward_analysis",
        "payload": {"address": address, "chain": "bsc", "mode": "deep"},
        "timeout": 600,
    }
    await redis.lpush("wm:task_queue", json.dumps(task))

    return {
        "analysis_id": analysis_id,
        "address": address,
        "type": "forward",
        "status": "pending",
        "message": "Forward inference started",
    }
