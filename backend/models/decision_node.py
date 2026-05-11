from dataclasses import dataclass, field
from typing import Dict, Optional
from datetime import datetime


@dataclass
class DecisionNode:
    id: str
    round_id: str
    node_type: str  # INITIAL_BUY, ADD_POSITION, REDUCE, EXIT, HOLD, STOP_LOSS, LEVERAGE, BRIDGE, LP_JOIN, LP_EXIT
    timestamp: Optional[datetime] = None
    token_address: str = ""
    token_symbol: str = ""
    price_at_decision: float = 0
    price_change_pct: float = 0
    market_cap: float = 0
    liquidity_depth: float = 0
    holder_count: int = 0
    volume_24h: float = 0
    social_mentions: int = 0
    btc_trend: str = ""
    market_sentiment: str = ""
    position_size_pct: float = 0
    inferred_logic: str = ""
    factor_scores: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {k: v for k, v in self.__dict__.items()}
