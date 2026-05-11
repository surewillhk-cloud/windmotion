from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ReplayData:
    analysis_id: str
    whale_address: str
    token_symbol: str
    start_date: str
    end_date: str
    rounds: List[Dict] = field(default_factory=list)
    price_data: List[Dict] = field(default_factory=list)
    narrative_segments: List[Dict] = field(default_factory=list)
    probability_curve: List[Dict] = field(default_factory=list)
    deliberation_markers: List[Dict] = field(default_factory=list)
    signal_layers: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {k: v for k, v in self.__dict__.items()}
