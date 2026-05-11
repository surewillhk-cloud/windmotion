"""Timeout and Circuit Breaker management."""
import time
import logging
from typing import Dict, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class CircuitBreaker:
    name: str
    failure_threshold: int = 3
    cooldown_s: int = 30
    failures: int = 0
    last_failure: float = 0
    is_open: bool = False

    def record_failure(self):
        self.failures += 1
        self.last_failure = time.time()
        if self.failures >= self.failure_threshold:
            self.is_open = True
            logger.warning(f"Circuit breaker {self.name} OPEN after {self.failures} failures")

    def record_success(self):
        self.failures = 0
        self.is_open = False

    def check(self) -> bool:
        if not self.is_open:
            return True
        if time.time() - self.last_failure > self.cooldown_s:
            self.is_open = False
            self.failures = 0
            logger.info(f"Circuit breaker {self.name} HALF-OPEN, cooldown expired")
            return True
        return False


class TimeoutManager:
    """Manages timeouts and circuit breakers for the pipeline."""

    def __init__(self, config: Dict):
        self.phase_timeouts = config.get("phase_timeouts", {})
        self.skill_timeouts = config.get("skill_timeouts", {})
        self.global_timeout = config.get("global_timeout", 600)
        cb_config = config.get("circuit_breaker", {})
        self.cb_threshold = cb_config.get("consecutive_failures", 3)
        self.cb_cooldown = cb_config.get("cooldown_s", 30)
        self.breakers: Dict[str, CircuitBreaker] = {}

    def get_phase_timeout(self, phase: str) -> int:
        return self.phase_timeouts.get(phase, 60)

    def get_skill_timeout(self, skill: str) -> int:
        return self.skill_timeouts.get(skill, 30)

    def get_breaker(self, name: str) -> CircuitBreaker:
        if name not in self.breakers:
            self.breakers[name] = CircuitBreaker(
                name=name,
                failure_threshold=self.cb_threshold,
                cooldown_s=self.cb_cooldown
            )
        return self.breakers[name]

    def check_api_call(self, provider: str) -> bool:
        return self.get_breaker(provider).check()

    def record_api_success(self, provider: str):
        self.get_breaker(provider).record_success()

    def record_api_failure(self, provider: str):
        self.get_breaker(provider).record_failure()

    def get_degraded_timeout(self, phase: str) -> int:
        """Get reduced timeout for degraded mode."""
        normal = self.get_phase_timeout(phase)
        return max(int(normal * 0.5), 15)
