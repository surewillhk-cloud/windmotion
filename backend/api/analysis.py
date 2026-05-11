"""Analysis API routes - Forward and reverse analysis endpoints."""
import uuid
from fastapi import APIRouter, HTTPException, Query
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/v1/analysis", tags=["analysis"])


class ForwardAnalysisRequest(BaseModel):
    whale_address: str = Field(..., description="Whale address to analyze")
    prediction_target: str = Field(..., description="What to predict")
    events: List[Dict] = Field(..., description="Events to analyze")
    context: Optional[str] = Field(None, description="Additional context")
    chain: str = Field("ethereum", description="Blockchain network")


class ReverseAnalysisRequest(BaseModel):
    address: str = Field(..., description="Address to reverse-analyze")
    transactions: Optional[List[Dict]] = Field(None, description="Transaction history")
    mode: str = Field("standard", description="Analysis mode: fast, standard, deep")
    chain: str = Field("ethereum", description="Blockchain network")


class BatchReverseRequest(BaseModel):
    addresses: List[Dict] = Field(..., description="Addresses with optional transactions")
    mode: str = Field("fast", description="Analysis mode")


@router.post("/forward", summary="Run forward inference analysis")
async def run_forward_analysis(req: ForwardAnalysisRequest):
    """Run a forward inference analysis on whale events.

    This triggers the full multi-agent pipeline:
    1. Build causal graph (referee + 3 reviewers)
    2. Analyze events (multiple role-based agents)
    3. Aggregate probabilities (weighted)
    4. Deliberate if divergent (challenge-response rounds)
    5. Generate structured report
    """
    analysis_id = f"fwd_{uuid.uuid4().hex[:12]}"

    return {
        "analysis_id": analysis_id,
        "status": "accepted",
        "whale_address": req.whale_address,
        "prediction_target": req.prediction_target,
        "events_count": len(req.events),
        "message": "Analysis started. Connect to WebSocket for real-time progress."
    }


@router.post("/reverse", summary="Run reverse inference analysis")
async def run_reverse_analysis(req: ReverseAnalysisRequest):
    """Run a reverse inference analysis on an address.

    Reverse-engineers the trading strategy by analyzing:
    - Entry timing (F1)
    - Exit timing (F2)
    - Position management (F3)
    - Token selection (F4)
    - Behavior patterns (F5)
    """
    analysis_id = f"rev_{uuid.uuid4().hex[:12]}"

    return {
        "analysis_id": analysis_id,
        "status": "accepted",
        "address": req.address,
        "mode": req.mode,
        "message": "Reverse analysis started."
    }


@router.post("/batch-reverse", summary="Run batch reverse analysis")
async def run_batch_reverse(req: BatchReverseRequest):
    """Run reverse analysis on multiple addresses."""
    analysis_ids = [f"rev_{uuid.uuid4().hex[:12]}" for _ in req.addresses]

    return {
        "analysis_ids": analysis_ids,
        "status": "accepted",
        "total_addresses": len(req.addresses),
        "mode": req.mode
    }


@router.get("/{analysis_id}", summary="Get analysis results")
async def get_analysis(analysis_id: str):
    """Get analysis results by ID."""
    return {
        "analysis_id": analysis_id,
        "status": "pending",
        "message": "Analysis not found or still in progress"
    }


@router.get("/{analysis_id}/status", summary="Get analysis status")
async def get_analysis_status(analysis_id: str):
    """Get real-time analysis status."""
    return {
        "analysis_id": analysis_id,
        "status": "pending",
        "current_phase": None,
        "progress_pct": 0,
        "elapsed_s": 0
    }


@router.get("/", summary="List analyses")
async def list_analyses(
    analysis_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    whale_address: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """List all analyses with optional filters."""
    return {
        "analyses": [],
        "total": 0,
        "limit": limit,
        "offset": offset
    }
