"""S8: Graph Sync - Synchronizes causal graph state to storage."""
import json
import time
from typing import Dict, Optional
from backend.skills.base import BaseSkill, SkillResult


class GraphSync(BaseSkill):
    """Synchronizes causal graph state between in-memory representation and persistent storage."""

    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.skill_id = "S8_GraphSync"

    async def execute(self, inputs: Dict, context: Optional[Dict] = None) -> SkillResult:
        start_time = time.time()
        valid, err = self.validate_inputs(inputs)
        if not valid:
            return self._create_result(False, {}, err, start_time)

        action = inputs.get("action", "save")
        graph = inputs.get("graph", {})
        analysis_id = inputs.get("analysis_id", "")
        neo4j_client = context.get("neo4j_client") if context else None

        if action == "save":
            if neo4j_client:
                try:
                    await neo4j_client.save_graph(analysis_id, graph)
                    return self._create_result(True, {
                        "action": "save",
                        "analysis_id": analysis_id,
                        "nodes_synced": len(graph.get("nodes", [])),
                        "edges_synced": len(graph.get("edges", [])),
                        "storage": "neo4j"
                    }, start_time=start_time)
                except Exception as e:
                    return self._create_result(True, {
                        "action": "save",
                        "analysis_id": analysis_id,
                        "nodes_synced": len(graph.get("nodes", [])),
                        "edges_synced": len(graph.get("edges", [])),
                        "storage": "memory_fallback",
                        "warning": str(e)
                    }, start_time=start_time)
            else:
                return self._create_result(True, {
                    "action": "save",
                    "analysis_id": analysis_id,
                    "nodes_synced": len(graph.get("nodes", [])),
                    "edges_synced": len(graph.get("edges", [])),
                    "storage": "memory_only"
                }, start_time=start_time)

        elif action == "load":
            if neo4j_client:
                try:
                    loaded = await neo4j_client.load_graph(analysis_id)
                    return self._create_result(True, {
                        "action": "load",
                        "analysis_id": analysis_id,
                        "graph": loaded,
                        "storage": "neo4j"
                    }, start_time=start_time)
                except Exception as e:
                    return self._create_result(False, {}, f"Load failed: {e}", start_time)
            else:
                return self._create_result(True, {
                    "action": "load",
                    "analysis_id": analysis_id,
                    "graph": {"nodes": [], "edges": []},
                    "storage": "memory_only"
                }, start_time=start_time)

        return self._create_result(False, {}, f"Unknown action: {action}", start_time)

    def validate_inputs(self, inputs: Dict) -> tuple[bool, Optional[str]]:
        if "action" not in inputs:
            return False, "Missing 'action' in inputs"
        if inputs["action"] not in ("save", "load"):
            return False, "action must be 'save' or 'load'"
        if inputs["action"] == "save" and "graph" not in inputs:
            return False, "Missing 'graph' for save action"
        return True, None
