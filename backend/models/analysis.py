from dataclasses import dataclass, field
from typing import Optional, Dict, List
from datetime import datetime
from enum import Enum


class AnalysisType(Enum):
    FORWARD = "forward"
    REVERSE = "reverse"


class AnalysisStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Analysis:
    id: str
    whale_address: str
    analysis_type: AnalysisType
    status: AnalysisStatus = AnalysisStatus.PENDING
    mode: str = "deep"  # fast, standard, deep
    chain: str = "bsc"
    progress_pct: float = 0
    current_phase: str = ""
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_s: float = 0
    report: Optional[Dict] = None
    graph: Optional[Dict] = None
    probability_timeline: List[Dict] = field(default_factory=list)
    deliberation_records: List[Dict] = field(default_factory=list)
    factor_scores: Optional[Dict] = None
    matched_patterns: List[Dict] = field(default_factory=list)
    error: Optional[str] = None
    metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "whale_address": self.whale_address,
            "analysis_type": self.analysis_type.value,
            "status": self.status.value,
            "mode": self.mode,
            "chain": self.chain,
            "progress_pct": self.progress_pct,
            "current_phase": self.current_phase,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_s": self.duration_s,
            "report": self.report,
            "factor_scores": self.factor_scores,
            "matched_patterns": self.matched_patterns,
            "error": self.error,
            "metadata": self.metadata
        }
