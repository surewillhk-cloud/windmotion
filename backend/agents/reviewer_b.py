"""Reviewer B Agent - Direction Detection for causal graphs."""
from typing import Dict, List
from backend.agents.base import BaseAgent


class ReviewerBAgent(BaseAgent):
    """审查AgentB - 方向检测专家。

    Responsibility: 检查每条因果关系的方向是否正确。
    """

    def __init__(self, config: Dict):
        super().__init__(config)

    def build_review_prompt(self, graph: Dict, context: str) -> str:
        edges_summary = "\n".join(
            f"- {e.get('source')} → {e.get('target')} | 关系: {e.get('relation', 'N/A')} | 强度: {e.get('strength', 'N/A')} | 证据: {e.get('evidence', 'N/A')}"
            for e in graph.get('edges', [])
        )
        return f"""## 任务：因果方向检测

### 当前因果边
{edges_summary}

### 分析上下文
{context}

### 检查要求
1. 每条因果关系的方向是否正确？（A→B 还是 B→A？）
2. 是否存在双向因果被简化为单向？
3. 是否存在相关性被误认为因果性？
4. 因果强度评分是否合理？

输出格式（JSON）：
{{
  "issues": [
    {{
      "edge_source": "node_a",
      "edge_target": "node_b",
      "issue_type": "wrong_direction|should_be_bidirectional|correlation_not_causation|wrong_strength",
      "description": "问题描述",
      "severity": "高/中/低",
      "suggested_fix": "建议修复"
    }}
  ],
  "suggestions": [
    {{
      "action": "reverse_edge|add_reverse|remove_edge|adjust_strength",
      "edge": {{"source": "...", "target": "..."}},
      "reason": "修改理由"
    }}
  ],
  "direction_accuracy_score": 1-10
}}"""
