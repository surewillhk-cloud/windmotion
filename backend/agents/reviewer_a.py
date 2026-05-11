"""Reviewer A Agent - Omission Detection for causal graphs."""
from typing import Dict, List
from backend.agents.base import BaseAgent


class ReviewerAAgent(BaseAgent):
    """审查AgentA - 遗漏检测专家。

    Responsibility: 检查因果图谱草案，找出被遗漏的重要因果路径。
    """

    def __init__(self, config: Dict):
        super().__init__(config)

    def build_review_prompt(self, graph: Dict, context: str) -> str:
        nodes_summary = "\n".join(
            f"- [{n.get('id')}] {n.get('label', 'N/A')} (类型: {n.get('type', 'N/A')}, 重要性: {n.get('importance', 'N/A')})"
            for n in graph.get('nodes', [])
        )
        edges_summary = "\n".join(
            f"- {e.get('source')} → {e.get('target')} ({e.get('relation', 'N/A')}, 强度: {e.get('strength', 'N/A')})"
            for e in graph.get('edges', [])
        )
        return f"""## 任务：因果图谱遗漏检测

### 当前图谱节点
{nodes_summary}

### 当前图谱边
{edges_summary}

### 分析上下文
{context}

### 检查要求
1. 是否有重要的因果路径被遗漏？
2. 是否有关键的中间变量未被纳入？
3. 是否有时间维度上的遗漏（延迟效应）？
4. 是否有外部因素未被考虑？

输出格式（JSON）：
{{
  "issues": [
    {{
      "type": "missing_path|missing_node|missing_temporal|missing_external",
      "description": "遗漏描述",
      "severity": "高/中/低",
      "suggested_fix": "建议的修复方案"
    }}
  ],
  "suggestions": [
    {{
      "action": "add_node|add_edge|modify_edge",
      "details": {{...}},
      "reason": "添加理由"
    }}
  ],
  "completeness_score": 1-10,
  "overall_assessment": "总体评估"
}}"""
