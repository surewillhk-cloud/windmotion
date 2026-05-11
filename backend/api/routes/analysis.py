"""Analysis API routes."""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional

router = APIRouter(prefix="/api/analysis", tags=["analysis"])


@router.get("/{analysis_id}")
async def get_analysis(analysis_id: str):
    """Get analysis details."""
    return {
        "id": analysis_id,
        "status": "pending",
        "type": "reverse",
        "whale_address": "",
        "progress_pct": 0,
        "current_phase": ""
    }


@router.get("/{analysis_id}/progress")
async def get_analysis_progress(analysis_id: str):
    """Get analysis progress."""
    return {
        "id": analysis_id,
        "status": "running",
        "progress_pct": 0,
        "current_phase": "",
        "phases": {}
    }


@router.get("/{analysis_id}/report")
async def get_analysis_report(analysis_id: str):
    """Get analysis report."""
    return {
        "id": analysis_id,
        "report": {},
        "status": "pending"
    }


@router.get("/{analysis_id}/replay")
async def get_analysis_replay(analysis_id: str):
    """Get replay data."""
    return {
        "id": analysis_id,
        "replay": {
            "rounds": [],
            "price_data": [],
            "narrative_segments": [],
            "probability_curve": []
        }
    }


@router.post("/{analysis_id}/cancel")
async def cancel_analysis(analysis_id: str):
    """Cancel running analysis."""
    return {"id": analysis_id, "status": "cancelled"}
