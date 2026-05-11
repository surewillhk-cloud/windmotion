"""Whale address model."""
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from datetime import datetime


@dataclass
class Whale:
    address: str
    chain: str = "bsc"
    total_profit_usd: float = 0
    realized_pnl: float = 0
    win_rate: float = 0
    roi: float = 0
    trade_count: int = 0
    token_count: int = 0
    last_active: Optional[datetime] = None
    labels: List[str] = field(default_factory=list)
    score: float = 0
    strategy_patterns: List[str] = field(default_factory=list)
    first_seen: Optional[datetime] = None
    metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "address": self.address,
            "chain": self.chain,
            "total_profit_usd": self.total_profit_usd,
            "realized_pnl": self.realized_pnl,
            "win_rate": self.win_rate,
            "roi": self.roi,
            "trade_count": self.trade_count,
            "token_count": self.token_count,
            "last_active": self.last_active.isoformat() if self.last_active else None,
            "labels": self.labels,
            "score": self.score,
            "strategy_patterns": self.strategy_patterns,
            "first_seen": self.first_seen.isoformat() if self.first_seen else None,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Whale":
        return cls(
            address=data["address"],
            chain=data.get("chain", "bsc"),
            total_profit_usd=data.get("total_profit_usd", 0),
            realized_pnl=data.get("realized_pnl", 0),
            win_rate=data.get("win_rate", 0),
            roi=data.get("roi", 0),
            trade_count=data.get("trade_count", 0),
            token_count=data.get("token_count", 0),
            labels=data.get("labels", []),
            score=data.get("score", 0),
            strategy_patterns=data.get("strategy_patterns", [])
        )
