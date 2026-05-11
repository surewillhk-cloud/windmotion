from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime


@dataclass
class Round:
    id: str
    token_address: str
    token_symbol: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    total_invested_usd: float = 0
    total_returned_usd: float = 0
    net_profit_usd: float = 0
    roi: float = 0
    max_drawdown_pct: float = 0
    avg_entry_price: float = 0
    avg_exit_price: float = 0
    trade_count: int = 0
    hold_days: int = 0
    transactions: List[Dict] = field(default_factory=list)
    decision_nodes: List[Dict] = field(default_factory=list)
    status: str = "completed"  # active, completed, partial

    def to_dict(self) -> Dict:
        return {k: v for k, v in self.__dict__.items()}
