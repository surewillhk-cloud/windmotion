from dataclasses import dataclass, field
from typing import List, Optional, Dict
from datetime import datetime


@dataclass
class Filter:
    id: str
    name: str
    chain: str = "bsc"
    min_trade_usd: float = 100000
    min_total_holdings_usd: float = 500000
    min_tokens: int = 5
    min_realized_profit_usd: float = 500000
    min_win_rate: float = 60
    min_profit_loss_ratio: float = 2.0
    min_profitable_tokens: int = 3
    min_profit_timespan_days: int = 30
    min_repeat_patterns: int = 2
    max_last_active_days: int = 7
    trade_frequency_range: List[int] = field(default_factory=lambda: [5, 200])
    exclude_contracts: bool = True
    exclude_exchange_wallets: bool = True
    exclude_mev_bots: bool = True
    token_whitelist: List[str] = field(default_factory=list)
    token_blacklist: List[str] = field(default_factory=list)
    auto_analyze: bool = False
    analyze_mode: str = "manual"  # manual, on_new, scheduled, on_complete
    analyze_frequency_hours: int = 6
    analyze_depth: str = "standard"  # fast, standard, deep
    concurrent_limit: int = 3
    cache_days: int = 7
    notify_on_complete: bool = False
    notify_on_high_score: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_dict(self) -> Dict:
        return {k: v for k, v in self.__dict__.items()}


@dataclass
class FilterResult:
    address: str
    total_profit_usd: float
    win_rate: float
    roi: float
    trade_count: int
    token_count: int
    last_active_days: int
    score: float
    labels: List[str] = field(default_factory=list)
