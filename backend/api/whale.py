"""Whale API routes - CRUD for whale addresses."""
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/v1/whales", tags=["whales"])


class WhaleCreateRequest(BaseModel):
    address: str = Field(..., description="Blockchain address")
    chain: str = Field("ethereum", description="Blockchain network")
    label: Optional[str] = Field(None, description="Human-readable label")
    tags: Optional[List[str]] = Field(None, description="Tags for categorization")


class WhaleUpdateRequest(BaseModel):
    label: Optional[str] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None


class WhaleScreenRequest(BaseModel):
    chain: Optional[str] = None
    min_volume_usd: float = Field(100000, ge=0)
    whale_type: Optional[str] = None
    tags: Optional[List[str]] = None
    limit: int = Field(50, ge=1, le=500)
    offset: int = Field(0, ge=0)


@router.post("/", summary="Add a whale address to track")
async def create_whale(req: WhaleCreateRequest):
    """Add a new whale address for tracking."""
    return {
        "status": "created",
        "address": req.address,
        "chain": req.chain,
        "label": req.label,
        "tags": req.tags or []
    }


@router.get("/", summary="List tracked whales")
async def list_whales(
    chain: Optional[str] = Query(None),
    whale_type: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0)
):
    """List all tracked whale addresses with optional filters."""
    return {
        "whales": [],
        "total": 0,
        "limit": limit,
        "offset": offset,
        "filters": {"chain": chain, "whale_type": whale_type}
    }


@router.get("/{address}", summary="Get whale details")
async def get_whale(address: str):
    """Get detailed information about a whale address."""
    return {
        "address": address,
        "chain": "ethereum",
        "label": None,
        "whale_type": "unknown",
        "total_volume_usd": 0,
        "transaction_count": 0,
        "tags": [],
        "risk_score": None
    }


@router.put("/{address}", summary="Update whale metadata")
async def update_whale(address: str, req: WhaleUpdateRequest):
    """Update whale address metadata."""
    return {
        "status": "updated",
        "address": address,
        "label": req.label,
        "tags": req.tags,
        "notes": req.notes
    }


@router.delete("/{address}", summary="Remove whale from tracking")
async def delete_whale(address: str):
    """Remove a whale address from tracking."""
    return {"status": "deleted", "address": address}


@router.post("/screen", summary="Screen for whale addresses")
async def screen_whales(req: WhaleScreenRequest):
    """Screen for whale addresses based on criteria."""
    return {
        "whales": [],
        "total": 0,
        "filters": {
            "chain": req.chain,
            "min_volume_usd": req.min_volume_usd,
            "whale_type": req.whale_type
        }
    }


@router.get("/{address}/transactions", summary="Get whale transactions")
async def get_whale_transactions(
    address: str,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """Get recent transactions for a whale address."""
    return {
        "address": address,
        "transactions": [],
        "total": 0,
        "limit": limit,
        "offset": offset
    }
