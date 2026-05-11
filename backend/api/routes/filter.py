"""Filter API routes with PostgreSQL backend."""
import json
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Request
from typing import Dict

router = APIRouter(prefix="/api/filters", tags=["filters"])


@router.get("")
async def list_filters(request: Request):
    """List all filters from PostgreSQL."""
    pg = request.app.state.pg
    rows = await pg.fetch(
        "SELECT * FROM filters ORDER BY created_at DESC"
    )
    return {"filters": rows, "total": len(rows)}


@router.post("")
async def create_filter(config: Dict, request: Request):
    """Create a new filter in PostgreSQL."""
    pg = request.app.state.pg
    now = datetime.now(timezone.utc)

    row = await pg.fetchrow(
        """
        INSERT INTO filters (name, chain, config, auto_analyze, analyze_mode,
                             analyze_frequency_hours, analyze_depth,
                             concurrent_limit, cache_days,
                             notify_on_complete, notify_on_high_score,
                             is_active, created_at, updated_at)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
        RETURNING *
        """,
        config.get("name", "Untitled"),
        config.get("chain", "bsc"),
        json.dumps(config.get("config", config)),
        config.get("auto_analyze", False),
        config.get("analyze_mode", "manual"),
        config.get("analyze_frequency_hours", 6),
        config.get("analyze_depth", "standard"),
        config.get("concurrent_limit", 3),
        config.get("cache_days", 7),
        config.get("notify_on_complete", False),
        config.get("notify_on_high_score", False),
        config.get("is_active", True),
        now,
        now,
    )
    return row


@router.get("/{filter_id}")
async def get_filter(filter_id: str, request: Request):
    """Get a single filter by ID."""
    pg = request.app.state.pg
    row = await pg.fetchrow("SELECT * FROM filters WHERE id = $1", filter_id)
    if not row:
        raise HTTPException(404, "Filter not found")
    return row


@router.put("/{filter_id}")
async def update_filter(filter_id: str, config: Dict, request: Request):
    """Update an existing filter."""
    pg = request.app.state.pg
    now = datetime.now(timezone.utc)

    existing = await pg.fetchrow("SELECT id FROM filters WHERE id = $1", filter_id)
    if not existing:
        raise HTTPException(404, "Filter not found")

    row = await pg.fetchrow(
        """
        UPDATE filters SET
            name = COALESCE($2, name),
            chain = COALESCE($3, chain),
            config = COALESCE($4, config),
            auto_analyze = COALESCE($5, auto_analyze),
            analyze_mode = COALESCE($6, analyze_mode),
            analyze_frequency_hours = COALESCE($7, analyze_frequency_hours),
            analyze_depth = COALESCE($8, analyze_depth),
            concurrent_limit = COALESCE($9, concurrent_limit),
            cache_days = COALESCE($10, cache_days),
            notify_on_complete = COALESCE($11, notify_on_complete),
            notify_on_high_score = COALESCE($12, notify_on_high_score),
            is_active = COALESCE($13, is_active),
            updated_at = $14
        WHERE id = $1
        RETURNING *
        """,
        filter_id,
        config.get("name"),
        config.get("chain"),
        json.dumps(config.get("config")) if "config" in config else None,
        config.get("auto_analyze"),
        config.get("analyze_mode"),
        config.get("analyze_frequency_hours"),
        config.get("analyze_depth"),
        config.get("concurrent_limit"),
        config.get("cache_days"),
        config.get("notify_on_complete"),
        config.get("notify_on_high_score"),
        config.get("is_active"),
        now,
    )
    return row


@router.delete("/{filter_id}")
async def delete_filter(filter_id: str, request: Request):
    """Delete a filter."""
    pg = request.app.state.pg
    result = await pg.execute("DELETE FROM filters WHERE id = $1", filter_id)
    if not result or result == "DELETE 0":
        raise HTTPException(404, "Filter not found")
    return {"deleted": filter_id}


@router.post("/{filter_id}/run")
async def run_filter(filter_id: str, request: Request):
    """Push a whale_screen task to Redis for the given filter."""
    pg = request.app.state.pg
    redis = request.app.state.redis

    row = await pg.fetchrow("SELECT * FROM filters WHERE id = $1", filter_id)
    if not row:
        raise HTTPException(404, "Filter not found")

    task = {
        "task_id": str(filter_id),
        "task_type": "whale_screen",
        "payload": {
            "filter_id": str(filter_id),
            "config": row.get("config", {}),
            "chain": row.get("chain", "bsc"),
        },
        "timeout": 600,
    }
    await redis.lpush("wm:task_queue", json.dumps(task))

    return {"filter_id": filter_id, "status": "running", "message": "Whale screen task queued"}


@router.get("/{filter_id}/results")
async def get_filter_results(filter_id: str, request: Request):
    """Get cached filter results from Redis, or empty if not yet available."""
    pg = request.app.state.pg
    redis = request.app.state.redis

    existing = await pg.fetchrow("SELECT id FROM filters WHERE id = $1", filter_id)
    if not existing:
        raise HTTPException(404, "Filter not found")

    cached = await redis.get_json(f"filter:{filter_id}:results")
    if cached:
        return cached
    return {"filter_id": filter_id, "results": [], "total": 0}
