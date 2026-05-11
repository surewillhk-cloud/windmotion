"""S1: Causal Graph Build - Builds and refines causal graphs through multi-agent review."""
import json
import os
import time
from typing import Dict, List, Optional
from backend.skills.base import BaseSkill, SkillResult


class CausalGraphBuild(BaseSkill):
    """Builds causal graphs through a 3-step process:
    1. Referee drafts initial graph
    2. Three reviewers check for omissions, direction errors, and missing variables
    3. Referee merges review results into final graph
    """

    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.skill_id = "S1_CausalGraphBuild"
        self.assignments = self._load_assignments()

    def _load_assignments(self) -> Dict:
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'skill_assignments.json')
        try:
            with open(config_path, 'r') as f:
                data = json.load(f)
                return data.get("S1_CausalGraphBuild", {})
        except FileNotFoundError:
            return {}

    async def execute(self, inputs: Dict, context: Optional[Dict] = None) -> SkillResult:
        start_time = time.time()
        valid, err = self.validate_inputs(inputs)
        if not valid:
            return self._create_result(False, {}, err, start_time)

        events = inputs.get("events", [])
        analysis_context = inputs.get("context", "")
        agent_pool = context.get("agent_pool") if context else None
        llm_caller = context.get("llm_caller") if context else None

        if not agent_pool or not llm_caller:
            return self._create_result(False, {}, "Missing agent_pool or llm_caller in context", start_time)

        # Step 1: Referee drafts initial graph
        referee = agent_pool.get("referee")
        draft_prompt = referee.build_graph_draft_prompt(events, analysis_context)
        draft_result = await llm_caller(
            model_tier="heavy",
            system_prompt=referee.get_system_prompt(),
            user_message=draft_prompt,
            task_type="graph_draft"
        )

        if not draft_result.get("success"):
            return self._create_result(False, {}, f"Draft generation failed: {draft_result.get('error')}", start_time)

        draft_graph = draft_result.get("data", {})

        # Step 2: Three reviewers analyze the draft
        reviewers = [
            ("reviewer_a", "omission"),
            ("reviewer_b", "direction"),
            ("reviewer_c", "variables")
        ]
        reviews = []
        for reviewer_id, dimension in reviewers:
            reviewer = agent_pool.get(reviewer_id)
            if not reviewer:
                continue
            review_prompt = reviewer.build_review_prompt(draft_graph, analysis_context)
            review_result = await llm_caller(
                model_tier="medium",
                system_prompt=reviewer.get_system_prompt(),
                user_message=review_prompt,
                task_type="graph_review"
            )
            if review_result.get("success"):
                review_data = review_result.get("data", {})
                review_data["agent_name"] = reviewer.name
                review_data["dimension"] = dimension
                reviews.append(review_data)

        # Step 3: Referee merges reviews
        merge_prompt = referee.build_merge_prompt(draft_graph, reviews)
        merge_result = await llm_caller(
            model_tier="heavy",
            system_prompt=referee.get_system_prompt(),
            user_message=merge_prompt,
            task_type="graph_merge"
        )

        if not merge_result.get("success"):
            return self._create_result(False, {}, f"Merge failed: {merge_result.get('error')}", start_time)

        final_graph = merge_result.get("data", {})
        return self._create_result(True, {
            "draft": draft_graph,
            "reviews": reviews,
            "final_graph": final_graph,
            "graph": final_graph.get("revised_graph", draft_graph),
            "probability": final_graph.get("final_probability", 50),
            "confidence": final_graph.get("confidence", "中")
        }, start_time=start_time)

    def validate_inputs(self, inputs: Dict) -> tuple[bool, Optional[str]]:
        if "events" not in inputs:
            return False, "Missing 'events' in inputs"
        if not isinstance(inputs["events"], list):
            return False, "'events' must be a list"
        return True, None
