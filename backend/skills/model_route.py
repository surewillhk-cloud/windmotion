"""S10: Model Router - Routes tasks to appropriate model tiers."""
import json
import os
from typing import Dict, Optional
from backend.skills.base import BaseSkill, SkillResult


class ModelRouter(BaseSkill):
    """Routes model calls to appropriate tier with fallback support."""

    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.routing_config = self._load_config()
        self.circuit_breakers: Dict[str, Dict] = {}

    def _load_config(self) -> Dict:
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'model_routing.json')
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return self.config.get('model_routing', {})

    async def execute(self, inputs: Dict, context: Optional[Dict] = None) -> SkillResult:
        task_type = inputs.get("task_type", "default")
        tier = self.routing_config.get("task_mapping", {}).get(task_type, "medium")
        return self._create_result(True, {"tier": tier, "config": self._get_tier_config(tier)})

    def validate_inputs(self, inputs: Dict) -> tuple:
        if "task_type" not in inputs:
            return False, "Missing task_type"
        return True, None

    def get_tier_for_task(self, task_type: str) -> str:
        return self.routing_config.get("task_mapping", {}).get(task_type, "medium")

    def get_model_config(self, tier: str) -> Dict:
        return self._get_tier_config(tier)

    def _get_tier_config(self, tier: str) -> Dict:
        tiers = self.routing_config.get("tiers", {})
        tier_config = tiers.get(tier, tiers.get("medium", {}))
        primary = tier_config.get("primary", {})
        fallback = tier_config.get("fallback", {})
        return {
            "primary": primary,
            "fallback": fallback,
            "tier": tier
        }

    def is_circuit_broken(self, provider: str) -> bool:
        breaker = self.circuit_breakers.get(provider, {})
        if not breaker.get("broken", False):
            return False
        import time
        if time.time() - breaker.get("broken_at", 0) > 30:
            breaker["broken"] = False
            return False
        return True

    def record_failure(self, provider: str):
        if provider not in self.circuit_breakers:
            self.circuit_breakers[provider] = {"failures": 0, "broken": False}
        cb = self.circuit_breakers[provider]
        cb["failures"] += 1
        if cb["failures"] >= 3:
            cb["broken"] = True
            import time
            cb["broken_at"] = time.time()

    def record_success(self, provider: str):
        if provider in self.circuit_breakers:
            self.circuit_breakers[provider]["failures"] = 0
            self.circuit_breakers[provider]["broken"] = False
