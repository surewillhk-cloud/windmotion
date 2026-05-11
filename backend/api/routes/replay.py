"""Replay API routes."""
from fastapi import APIRouter

router = APIRouter(prefix="/api/replay", tags=["replay"])


@router.get("/{analysis_id}")
async def get_replay(analysis_id: str):
    return {
        "analysis_id": analysis_id,
        "rounds": [],
        "price_data": [],
        "narrative_segments": [],
        "probability_curve": [],
        "deliberation_markers": []
    }


@router.get("/{analysis_id}/cases")
async def list_cases():
    """List available embed cases."""
    return {"cases": []}
