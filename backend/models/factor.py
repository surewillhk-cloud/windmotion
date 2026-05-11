from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Factor:
    id: str  # F1-F5
    name: str
    name_zh: str
    description: str
    sub_factors: List[str] = field(default_factory=list)


@dataclass
class FactorScore:
    factor_id: str
    score: float  # 0-5
    sub_scores: Dict[str, float] = field(default_factory=dict)
    summary: str = ""
    evidence: List[str] = field(default_factory=list)


FACTOR_DEFINITIONS = [
    Factor("F1", "Entry Timing", "入场时机", "买入时机的质量评估",
           ["price_vs_30d", "price_vs_ath", "listing_days", "market_cap_at_buy"]),
    Factor("F2", "Exit Timing", "出场时机", "卖出时机的质量评估",
           ["sell_vs_ath", "price_change_30d_after", "batch_selling", "decisiveness"]),
    Factor("F3", "Position Management", "仓位管理", "仓位控制能力评估",
           ["initial_position_pct", "batch_building", "add_logic", "max_position", "drawdown_behavior"]),
    Factor("F4", "Token Selection", "Token选择", "Token质量评估",
           ["listing_days", "market_cap", "holder_growth", "liquidity", "narrative", "security"]),
    Factor("F5", "Behavior Pattern", "行为模式", "交易行为模式评估",
           ["trade_frequency", "leverage_usage", "defi_participation", "fund_flow", "mev"]),
]
