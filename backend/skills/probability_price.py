"""S3: Probability Price - Weighted probability aggregation across agents."""
import json
import os
import time
import math
from typing import Dict, List, Optional
from backend.skills.base import BaseSkill, SkillResult


class ProbabilityPrice(BaseSkill):
    """Aggregates probability estimates from multiple agents using weighted averaging.

    Weight scheme:
    - B agents (analysts): 2.0x
    - C institutional: 1.5x
    - C others (retail/social): 1.0x
    """

    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.skill_id = "S3_ProbabilityPrice"
        self.config_data = self._load_config()

    def _load_config(self) -> Dict:
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'skill_assignments.json')
        try:
            with open(config_path, 'r') as f:
                data = json.load(f)
                return data.get("S3_ProbabilityPrice", {})
        except FileNotFoundError:
            return {}

    async def execute(self, inputs: Dict, context: Optional[Dict] = None) -> SkillResult:
        start_time = time.time()
        valid, err = self.validate_inputs(inputs)
        if not valid:
            return self._create_result(False, {}, err, start_time)

        agent_results = inputs.get("agent_results", [])
        weight_map = self.config_data.get("weight_map", {"B": 2.0, "C_institutional": 1.5, "C_others": 1.0})
        std_dev_threshold = self.config_data.get("std_dev_threshold", 5)

        weighted_sum = 0.0
        total_weight = 0.0
        probabilities = []

        for result in agent_results:
            prob = result.get("probability_estimate", 50)
            agent_type = result.get("agent_type", "C")
            agent_id = result.get("agent_id", "")

            if agent_type == "B":
                weight = weight_map.get("B", 2.0)
            elif agent_id == "institutional":
                weight = weight_map.get("C_institutional", 1.5)
            else:
                weight = weight_map.get("C_others", 1.0)

            weighted_sum += prob * weight
            total_weight += weight
            probabilities.append({"agent_id": agent_id, "probability": prob, "weight": weight})

        weighted_avg = round(weighted_sum / total_weight) if total_weight > 0 else 50

        # Calculate standard deviation
        if len(probabilities) > 1:
            mean = weighted_avg
            variance = sum((p["probability"] - mean) ** 2 for p in probabilities) / len(probabilities)
            std_dev = math.sqrt(variance)
        else:
            std_dev = 0.0

        # Detect divergent agents (beyond threshold)
        divergent_agents = []
        for p in probabilities:
            if abs(p["probability"] - weighted_avg) > std_dev_threshold * 2:
                divergent_agents.append({
                    "agent_id": p["agent_id"],
                    "probability": p["probability"],
                    "deviation": p["probability"] - weighted_avg
                })

        # Find most divergent pair
        most_divergent_pair = None
        if len(probabilities) >= 2:
            sorted_probs = sorted(probabilities, key=lambda x: x["probability"])
            most_divergent_pair = {
                "low": {"agent_id": sorted_probs[0]["agent_id"], "probability": sorted_probs[0]["probability"]},
                "high": {"agent_id": sorted_probs[-1]["agent_id"], "probability": sorted_probs[-1]["probability"]},
                "spread": sorted_probs[-1]["probability"] - sorted_probs[0]["probability"]
            }

        return self._create_result(True, {
            "weighted_probability": weighted_avg,
            "std_dev": round(std_dev, 2),
            "agent_probabilities": probabilities,
            "divergent_agents": divergent_agents,
            "most_divergent_pair": most_divergent_pair,
            "spread": most_divergent_pair["spread"] if most_divergent_pair else 0,
            "needs_deliberation": (most_divergent_pair and most_divergent_pair["spread"] > std_dev_threshold * 3) if most_divergent_pair else False
        }, start_time=start_time)

    def validate_inputs(self, inputs: Dict) -> tuple[bool, Optional[str]]:
        if "agent_results" not in inputs:
            return False, "Missing 'agent_results' in inputs"
        if not isinstance(inputs["agent_results"], list):
            return False, "'agent_results' must be a list"
        return True, None
