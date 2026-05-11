"""Reverse API routes - Dedicated reverse inference endpoints."""
from fastapi import APIRouter, HTTPException, Query
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/v1/reverse", tags=["reverse"])


class FactorAnalysisRequest(BaseModel):
    address: str = Field(..., description="Address to analyze")
    transactions: Optional[List[Dict]] = None
    price_data: Optional[Dict] = None
    mode: str = Field("standard", description="fast, standard, deep")


class StrategyMatchRequest(BaseModel):
    factors: Dict = Field(..., description="Factor scores F1-F5")
    address: Optional[str] = None


class CompareRequest(BaseModel):
    addresses: List[str] = Field(..., description="Addresses to compare")
    mode: str = Field("fast", description="Analysis mode")


@router.post("/factors", summary="Analyze trading factors")
async def analyze_factors(req: FactorAnalysisRequest):
    """Analyze the 5 core trading factors for an address.

    Factors:
    - F1: Entry Timing
    - F2: Exit Timing
    - F3: Position Management
    - F4: Token Selection
    - F5: Behavior Pattern
    """
    return {
        "address": req.address,
        "mode": req.mode,
        "factors": {
            "F1_entry_timing": {"score": 0, "details": {}},
            "F2_exit_timing": {"score": 0, "details": {}},
            "F3_position_management": {"score": 0, "details": {}},
            "F4_token_selection": {"score": 0, "details": {}},
            "F5_behavior_pattern": {"score": 0, "details": {}}
        },
        "status": "pending"
    }


@router.post("/strategies", summary="Match strategy patterns")
async def match_strategies(req: StrategyMatchRequest):
    """Match factor scores against known strategy patterns."""
    return {
        "address": req.address,
        "matched_strategies": [],
        "factors": req.factors
    }


@router.post("/compare", summary="Compare multiple addresses")
async def compare_addresses(req: CompareRequest):
    """Compare trading factors across multiple addresses."""
    return {
        "addresses": req.addresses,
        "comparisons": [],
        "rankings": []
    }


@router.get("/strategies", summary="List available strategy patterns")
async def list_strategies():
    """List all available strategy patterns."""
    return {
        "strategies": [
            {"id": "early_bird", "name": "Early Bird", "name_zh": "早期发现者"},
            {"id": "top_catcher", "name": "Top Catcher", "name_zh": "精准逃顶"},
            {"id": "dca_master", "name": "DCA Master", "name_zh": "定投大师"},
            {"id": "diamond_hands", "name": "Diamond Hands", "name_zh": "钻石手"},
            {"id": "leverage_player", "name": "Leverage Player", "name_zh": "杠杆玩家"},
            {"id": "lp_farmer", "name": "LP Farmer", "name_zh": "流动性矿工"},
            {"id": "cross_chain_hunter", "name": "Cross-Chain Hunter", "name_zh": "跨链猎手"},
            {"id": "meme_hunter", "name": "Meme Hunter", "name_zh": "Meme猎手"},
            {"id": "defi_native", "name": "DeFi Native", "name_zh": "DeFi原住民"},
            {"id": "sniper", "name": "Sniper", "name_zh": "抢跑者"},
        ]
    }


@router.get("/decision-nodes", summary="List decision node types")
async def list_decision_nodes():
    """List all supported decision node types."""
    return {
        "node_types": [
            "INITIAL_BUY", "ADD_POSITION", "REDUCE", "EXIT",
            "HOLD", "STOP_LOSS", "LEVERAGE", "BRIDGE", "LP_JOIN", "LP_EXIT"
        ]
    }
