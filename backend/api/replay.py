"""Replay API routes - Transaction replay and simulation."""
import uuid
from fastapi import APIRouter, HTTPException, Query
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/v1/replay", tags=["replay"])


class ReplayCreateRequest(BaseModel):
    address: str = Field(..., description="Address to replay")
    replay_type: str = Field("full", description="full, partial, what_if")
    time_range_start: Optional[str] = None
    time_range_end: Optional[str] = None
    settings: Optional[Dict] = None


class WhatIfRequest(BaseModel):
    address: str = Field(..., description="Address to simulate")
    scenario: Dict = Field(..., description="What-if scenario parameters")
    time_range_start: Optional[str] = None
    time_range_end: Optional[str] = None


@router.post("/", summary="Create a transaction replay")
async def create_replay(req: ReplayCreateRequest):
    """Create a new transaction replay session."""
    replay_id = f"replay_{uuid.uuid4().hex[:12]}"

    return {
        "replay_id": replay_id,
        "status": "created",
        "address": req.address,
        "replay_type": req.replay_type
    }


@router.get("/{replay_id}", summary="Get replay results")
async def get_replay(replay_id: str):
    """Get replay session results."""
    return {
        "replay_id": replay_id,
        "status": "pending",
        "total_steps": 0,
        "completed_steps": 0
    }


@router.get("/{replay_id}/steps", summary="Get replay steps")
async def get_replay_steps(
    replay_id: str,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """Get individual steps of a replay."""
    return {
        "replay_id": replay_id,
        "steps": [],
        "total": 0,
        "limit": limit,
        "offset": offset
    }


@router.post("/what-if", summary="Run what-if simulation")
async def run_what_if(req: WhatIfRequest):
    """Run a what-if simulation with modified parameters."""
    replay_id = f"whatif_{uuid.uuid4().hex[:12]}"

    return {
        "replay_id": replay_id,
        "status": "accepted",
        "address": req.address,
        "scenario": req.scenario
    }


@router.get("/", summary="List replays")
async def list_replays(
    address: Optional[str] = Query(None),
    replay_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """List all replay sessions."""
    return {
        "replays": [],
        "total": 0,
        "limit": limit,
        "offset": offset
    }
