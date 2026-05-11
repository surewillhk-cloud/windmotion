"""S4: Deliberate - Multi-round deliberation between divergent agents."""
import json
import os
import time
from typing import Dict, List, Optional
from backend.skills.base import BaseSkill, SkillResult


class Deliberate(BaseSkill):
    """Manages deliberation rounds between agents with divergent probability estimates.

    Process:
    1. Identify most divergent agent pair
    2. Round 1: Challenge phase - each questions the other's reasoning
    3. Round 2: Response phase - each responds and updates probability
    4. Referee makes final ruling
    """

    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.skill_id = "S4_Deliberate"
        self.config_data = self._load_config()

    def _load_config(self) -> Dict:
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'skill_assignments.json')
        try:
            with open(config_path, 'r') as f:
                data = json.load(f)
                return data.get("S4_Deliberate", {})
        except FileNotFoundError:
            return {}

    def _should_deliberate(self, inputs: Dict) -> bool:
        """Check if deliberation should be triggered."""
        deliberation_rules_path = os.path.join(
            os.path.dirname(__file__), '..', 'config', 'deliberation_rules.json'
        )
        try:
            with open(deliberation_rules_path, 'r') as f:
                rules = json.load(f)
        except FileNotFoundError:
            rules = {}

        trigger = rules.get("trigger_conditions", {})
        spread = inputs.get("spread", 0)
        threshold = trigger.get("max_spread_threshold", 30)

        if spread >= threshold:
            return True

        if inputs.get("probability_change_threshold"):
            change = abs(inputs.get("probability_change", 0))
            if change >= trigger.get("probability_change_threshold", 15):
                return True

        return False

    async def execute(self, inputs: Dict, context: Optional[Dict] = None) -> SkillResult:
        start_time = time.time()
        valid, err = self.validate_inputs(inputs)
        if not valid:
            return self._create_result(False, {}, err, start_time)

        if not self._should_deliberate(inputs):
            return self._create_result(True, {
                "deliberation_triggered": False,
                "reason": "Divergence within acceptable range",
                "final_probability": inputs.get("weighted_probability", 50)
            }, start_time=start_time)

        divergent_pair = inputs.get("most_divergent_pair", {})
        agent_results = inputs.get("agent_results", [])
        graph_snapshot = inputs.get("graph_snapshot", {"nodes": [], "edges": []})
        agent_pool = context.get("agent_pool") if context else None
        llm_caller = context.get("llm_caller") if context else None

        if not agent_pool or not llm_caller:
            return self._create_result(False, {}, "Missing agent_pool or llm_caller in context", start_time)

        # Get the two most divergent agents
        low_agent_id = divergent_pair.get("low", {}).get("agent_id", "")
        high_agent_id = divergent_pair.get("high", {}).get("agent_id", "")

        low_agent = agent_pool.get(low_agent_id)
        high_agent = agent_pool.get(high_agent_id)

        if not low_agent or not high_agent:
            return self._create_result(False, {}, "Could not find divergent agents", start_time)

        # Get their original results
        low_result = next((r for r in agent_results if r.get("agent_id") == low_agent_id), {})
        high_result = next((r for r in agent_results if r.get("agent_id") == high_agent_id), {})

        # Round 1: Challenge phase
        challenge_prompt_low = f"""## 任务：质疑对方的观点

你认为概率是 {low_result.get('probability_estimate', 50)}%。
{high_agent.name} 认为概率是 {high_result.get('probability_estimate', 50)}%。

对方的推理: {high_result.get('causal_analysis', high_result.get('reasoning', 'N/A'))}

请从你的角度质疑对方的分析，指出其逻辑漏洞或信息盲点。

输出格式（JSON）：
{{
  "challenge_point": "你的核心质疑点",
  "evidence_against": ["反面证据1", "反面证据2"],
  "suggested_probability": {low_result.get('probability_estimate', 50)},
  "reasoning": "质疑推理"
}}"""

        challenge_prompt_high = f"""## 任务：质疑对方的观点

你认为概率是 {high_result.get('probability_estimate', 50)}%。
{low_agent.name} 认为概率是 {low_result.get('probability_estimate', 50)}%。

对方的推理: {low_result.get('causal_analysis', low_result.get('reasoning', 'N/A'))}

请从你的角度质疑对方的分析，指出其逻辑漏洞或信息盲点。

输出格式（JSON）：
{{
  "challenge_point": "你的核心质疑点",
  "evidence_against": ["反面证据1", "反面证据2"],
  "suggested_probability": {high_result.get('probability_estimate', 50)},
  "reasoning": "质疑推理"
}}"""

        challenge_low = await llm_caller(
            model_tier=low_agent.model_tier,
            system_prompt=low_agent.get_system_prompt(),
            user_message=challenge_prompt_low,
            task_type="deliberation_challenge"
        )
        challenge_high = await llm_caller(
            model_tier=high_agent.model_tier,
            system_prompt=high_agent.get_system_prompt(),
            user_message=challenge_prompt_high,
            task_type="deliberation_challenge"
        )

        challenge_results = []
        if challenge_low.get("success"):
            cl_data = challenge_low.get("data", {})
            cl_data["agent_id"] = low_agent_id
            cl_data["agent_name"] = low_agent.name
            challenge_results.append(cl_data)
        if challenge_high.get("success"):
            ch_data = challenge_high.get("data", {})
            ch_data["agent_id"] = high_agent_id
            ch_data["agent_name"] = high_agent.name
            challenge_results.append(ch_data)

        # Round 2: Response phase
        response_results = []
        for challenger in challenge_results:
            target_id = high_agent_id if challenger["agent_id"] == low_agent_id else low_agent_id
            target_agent = agent_pool.get(target_id)
            if not target_agent:
                continue

            response_prompt = f"""## 任务：回应质疑并更新你的概率估计

对方的质疑: {challenger.get('challenge_point', 'N/A')}
反面证据: {challenger.get('evidence_against', [])}

请回应质疑，如果对方有道理就调整你的概率，如果没有就坚持并说明理由。

输出格式（JSON）：
{{
  "response": "你的回应",
  "probability": {low_result.get('probability_estimate', 50) if target_id == low_agent_id else high_result.get('probability_estimate', 50)},
  "adjustment_reason": "调整/不调整的理由",
  "key_concession": "你承认的对方观点（如有）"
}}"""

            resp = await llm_caller(
                model_tier=target_agent.model_tier,
                system_prompt=target_agent.get_system_prompt(),
                user_message=response_prompt,
                task_type="deliberation_challenge"
            )
            if resp.get("success"):
                r_data = resp.get("data", {})
                r_data["agent_id"] = target_id
                r_data["agent_name"] = target_agent.name
                response_results.append(r_data)

        # Referee ruling
        referee = agent_pool.get("referee")
        ruling_prompt = referee.build_ruling_prompt(challenge_results, response_results)
        ruling = await llm_caller(
            model_tier="heavy",
            system_prompt=referee.get_system_prompt(),
            user_message=ruling_prompt,
            task_type="deliberation_ruling"
        )

        ruling_data = ruling.get("data", {}) if ruling.get("success") else {}

        return self._create_result(True, {
            "deliberation_triggered": True,
            "round_1_challenges": challenge_results,
            "round_2_responses": response_results,
            "ruling": ruling_data,
            "final_probability": ruling_data.get("final_probability", inputs.get("weighted_probability", 50)),
            "confidence": ruling_data.get("confidence", "中")
        }, start_time=start_time)

    def validate_inputs(self, inputs: Dict) -> tuple[bool, Optional[str]]:
        if "agent_results" not in inputs:
            return False, "Missing 'agent_results' in inputs"
        if "most_divergent_pair" not in inputs:
            return False, "Missing 'most_divergent_pair' in inputs"
        return True, None
