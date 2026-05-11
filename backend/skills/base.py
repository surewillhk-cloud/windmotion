"""Skill Base Class - Defines the interface for all skills."""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import time


@dataclass
class SkillResult:
    """Standard skill execution result."""
    skill_id: str
    success: bool
    data: Dict
    error: Optional[str] = None
    execution_time_ms: int = 0
    token_usage: Optional[Dict] = None
    metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "skill_id": self.skill_id,
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "execution_time_ms": self.execution_time_ms,
            "token_usage": self.token_usage,
            "metadata": self.metadata,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }


class BaseSkill(ABC):
    """Base class for all skills."""

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.skill_id = self.__class__.__name__

    @abstractmethod
    async def execute(self, inputs: Dict, context: Optional[Dict] = None) -> SkillResult:
        pass

    @abstractmethod
    def validate_inputs(self, inputs: Dict) -> tuple[bool, Optional[str]]:
        pass

    def _create_result(self, success: bool, data: Dict, error: str = None,
                       start_time: float = None, **kwargs) -> SkillResult:
        elapsed = 0
        if start_time:
            elapsed = int((time.time() - start_time) * 1000)
        return SkillResult(
            skill_id=self.skill_id,
            success=success,
            data=data,
            error=error,
            execution_time_ms=elapsed,
            **kwargs
        )
