"""Phase Manager - Manages pipeline phase execution and transitions."""
import asyncio
import time
import logging
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class PhaseStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    TIMEOUT = "timeout"


@dataclass
class PhaseResult:
    phase_id: str
    status: PhaseStatus
    data: Dict = field(default_factory=dict)
    error: Optional[str] = None
    duration_s: float = 0
    metadata: Dict = field(default_factory=dict)


class PhaseManager:
    """Manages execution of pipeline phases with timeout and error handling."""

    def __init__(self, timeouts: Dict[str, int]):
        self.timeouts = timeouts
        self.results: Dict[str, PhaseResult] = {}
        self.current_phase: Optional[str] = None
        self._progress_callbacks: List[Callable] = []
        self._start_time: float = 0

    def on_progress(self, callback: Callable):
        self._progress_callbacks.append(callback)

    async def _notify_progress(self, phase_id: str, status: PhaseStatus, data: Dict = None):
        for cb in self._progress_callbacks:
            try:
                if asyncio.iscoroutinefunction(cb):
                    await cb(phase_id, status, data or {})
                else:
                    cb(phase_id, status, data or {})
            except Exception as e:
                logger.error(f"Progress callback error: {e}")

    async def execute_phase(self, phase_id: str, handler: Callable, inputs: Dict,
                           timeout_override: Optional[int] = None) -> PhaseResult:
        timeout = timeout_override or self.timeouts.get(phase_id, 60)
        self.current_phase = phase_id

        await self._notify_progress(phase_id, PhaseStatus.RUNNING)
        start = time.time()

        try:
            result = await asyncio.wait_for(handler(inputs), timeout=timeout)
            elapsed = time.time() - start
            phase_result = PhaseResult(
                phase_id=phase_id,
                status=PhaseStatus.COMPLETED,
                data=result if isinstance(result, dict) else {"result": result},
                duration_s=elapsed
            )
        except asyncio.TimeoutError:
            elapsed = time.time() - start
            phase_result = PhaseResult(
                phase_id=phase_id,
                status=PhaseStatus.TIMEOUT,
                error=f"Phase timed out after {timeout}s",
                duration_s=elapsed
            )
        except Exception as e:
            elapsed = time.time() - start
            phase_result = PhaseResult(
                phase_id=phase_id,
                status=PhaseStatus.FAILED,
                error=str(e),
                duration_s=elapsed
            )

        self.results[phase_id] = phase_result
        await self._notify_progress(phase_id, phase_result.status, phase_result.data)
        return phase_result

    async def execute_phases_sequential(self, phases: List[Dict]) -> Dict[str, PhaseResult]:
        for phase in phases:
            phase_id = phase["id"]
            handler = phase["handler"]
            inputs = phase.get("inputs", {})
            timeout = phase.get("timeout")

            result = await self.execute_phase(phase_id, handler, inputs, timeout)

            if result.status in (PhaseStatus.FAILED, PhaseStatus.TIMEOUT):
                if phase.get("required", True):
                    logger.error(f"Required phase {phase_id} failed: {result.error}")
                    break
                else:
                    logger.warning(f"Optional phase {phase_id} failed, continuing")

        return self.results

    async def execute_phases_parallel(self, phases: List[Dict]) -> Dict[str, PhaseResult]:
        tasks = []
        for phase in phases:
            phase_id = phase["id"]
            handler = phase["handler"]
            inputs = phase.get("inputs", {})
            timeout = phase.get("timeout")
            tasks.append(self.execute_phase(phase_id, handler, inputs, timeout))

        await asyncio.gather(*tasks, return_exceptions=True)
        return self.results

    def get_total_duration(self) -> float:
        return sum(r.duration_s for r in self.results.values())

    def get_summary(self) -> Dict:
        return {
            "phases": {
                pid: {"status": r.status.value, "duration_s": r.duration_s, "error": r.error}
                for pid, r in self.results.items()
            },
            "total_duration_s": self.get_total_duration(),
            "all_completed": all(r.status == PhaseStatus.COMPLETED for r in self.results.values())
        }
