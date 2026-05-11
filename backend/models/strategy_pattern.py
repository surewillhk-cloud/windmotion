from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class StrategyPattern:
    id: str
    name: str
    name_zh: str
    description: str
    conditions: Dict
    avg_roi_multiplier: float = 1.0
    matched: bool = False
    confidence: float = 0
    evidence: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {k: v for k, v in self.__dict__.items()}
