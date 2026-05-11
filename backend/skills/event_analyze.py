"""S2: Event Analyze - Multi-agent event analysis with role-based perspectives."""
import json
import os
import time
from typing import Dict, List, Optional
from backend.skills.base import BaseSkill, SkillResult


class EventAnalyze(BaseSkill):
    """Analyzes events using multiple agents based on event type and activation rules."""

    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.skill_id = "S2_EventAnalyze"
        self.assignments = self._load_assignments()

    def _load_assignments(self) -> Dict:
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'skill_assignments.json')
        try:
            with open(config_path, 'r') as f:
                data = json.load(f)
                return data.get("S2_EventAnalyze", {})
        except FileNotFoundError:
            return {}

    async def execute(self, inputs: Dict, context: Optional[Dict] = None) -> SkillResult:
        start_time = time.time()
        valid, err = self.validate_inputs(inputs)
        if not valid:
            return self._create_result(False, {}, err, start_time)

        event = inputs.get("event", {})
        graph_snapshot = inputs.get("graph_snapshot", {"nodes": [], "edges": []})
        analysis_context = inputs.get("context", "")
        agent_pool = context.get("agent_pool") if context else None
        llm_caller = context.get("llm_caller") if context else None

        if not agent_pool or not llm_caller:
            return self._create_result(False, {}, "Missing agent_pool or llm_caller in context", start_time)

        event_type = event.get("type", "default")
        activation_rules = self.assignments.get("activation_rules", {})
        agent_ids = activation_rules.get(event_type, activation_rules.get("default", []))

        min_agents = self.assignments.get("min_agents_per_event", 3)
        if len(agent_ids) < min_agents:
            default_agents = activation_rules.get("default", [])
            for aid in default_agents:
                if aid not in agent_ids:
                    agent_ids.append(aid)
                if len(agent_ids) >= min_agents:
                    break

        results = []
        for agent_id in agent_ids:
            agent = agent_pool.get(agent_id)
            if not agent:
                continue

            reasoning_input = agent.build_reasoning_input(event, analysis_context, graph_snapshot)
            task_type = "b_agent_reasoning" if agent.type == "B" else "c_agent_reasoning"

            llm_result = await llm_caller(
                model_tier=agent.model_tier,
                system_prompt=agent.get_system_prompt(),
                user_message=reasoning_input,
                task_type=task_type
            )

            if llm_result.get("success"):
                result_data = llm_result.get("data", {})
                result_data["agent_id"] = agent_id
                result_data["agent_name"] = agent.name
                result_data["agent_type"] = agent.type
                results.append(result_data)

                # Update agent profile
                prob = result_data.get("probability_estimate", 50)
                reason = result_data.get("causal_analysis", result_data.get("reasoning", ""))
                self_check = result_data.get("self_check", {})
                agent.profile.update_probability(prob, reason, self_check.get("deviation", ""))
                agent.profile.add_history(event.get("id", "unknown"), prob, reason, self_check)

        return self._create_result(True, {
            "event_id": event.get("id", "unknown"),
            "event_type": event_type,
            "agent_results": results,
            "agents_participated": len(results),
            "probability_range": {
                "min": min(r.get("probability_estimate", 50) for r in results) if results else 50,
                "max": max(r.get("probability_estimate", 50) for r in results) if results else 50,
                "avg": sum(r.get("probability_estimate", 50) for r in results) / len(results) if results else 50
            }
        }, start_time=start_time)

    def validate_inputs(self, inputs: Dict) -> tuple[bool, Optional[str]]:
        if "event" not in inputs:
            return False, "Missing 'event' in inputs"
        if not isinstance(inputs["event"], dict):
            return False, "'event' must be a dict"
        return True, None
